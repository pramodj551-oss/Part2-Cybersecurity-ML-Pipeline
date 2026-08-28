"""STEP 17 — Feature Engineering + Ablation Study.

This module is intentionally independent from the production prediction
pipeline.  It provides reproducible feature engineering and an ablation
experiment for the regression target used by this project.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import RANDOM_STATE
from src.data_loader import REQUIRED_COLUMNS


class FeatureEngineeringAblationStudy:
    """Create safe derived features and compare feature-group ablations."""

    target_column = "severity_score"

    def engineer_features(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        missing = [c for c in REQUIRED_COLUMNS if c not in dataframe.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df = dataframe.copy()
        df["incident_date"] = pd.to_datetime(df["incident_date"], errors="coerce")

        # Time-derived features use only incident metadata.
        df["incident_year"] = df["incident_date"].dt.year
        df["incident_month"] = df["incident_date"].dt.month
        df["incident_dayofweek"] = df["incident_date"].dt.dayofweek

        # Robust ratios and log transforms avoid division by zero.
        records = pd.to_numeric(df["records_affected"], errors="coerce")
        detection = pd.to_numeric(df["detection_time_hours"], errors="coerce")
        ransom = pd.to_numeric(df["ransom_demand_usd"], errors="coerce")
        df["log_records_affected"] = np.log1p(records.clip(lower=0))
        df["log_ransom_demand_usd"] = np.log1p(ransom.clip(lower=0))
        df["records_per_detection_hour"] = records / detection.replace(0, np.nan)
        df["ransom_per_record"] = ransom / records.replace(0, np.nan)
        df["advanced_attack_indicator"] = (
            pd.to_numeric(df["data_exfiltration"], errors="coerce").fillna(0)
            + pd.to_numeric(df["zero_day_used"], errors="coerce").fillna(0)
        )

        # Identifiers and target are never used as model inputs.
        return df.drop(columns=["incident_id", "incident_date"], errors="ignore")

    @staticmethod
    def _groups(df: pd.DataFrame) -> dict[str, list[str]]:
        target = {"severity_score"}
        base = [c for c in df.columns if c not in target and c not in {
            "downtime_hours", "response_team_size", "regulatory_fine_usd",
            "resolved_within_7_days",
        }]
        temporal = [c for c in base if c.startswith("incident_")]
        statistical = [c for c in base if c.startswith(("log_", "records_per_", "ransom_per_"))]
        network = [c for c in base if c in {
            "attack_type", "threat_actor", "sector", "region",
            "data_exfiltration", "zero_day_used", "advanced_attack_indicator",
        }]
        return {"base": base, "temporal": temporal, "statistical": statistical, "network": network}

    @staticmethod
    def _build_model(frame: pd.DataFrame) -> Pipeline:
        numeric = frame.select_dtypes(include=["number", "bool"]).columns.tolist()
        categorical = [c for c in frame.columns if c not in numeric]
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                                  ("scaler", StandardScaler())]), numeric),
                ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
            ],
            remainder="drop",
        )
        return Pipeline([
            ("preprocessor", preprocessor),
            ("model", RandomForestRegressor(
                n_estimators=120, random_state=RANDOM_STATE, n_jobs=-1
            )),
        ])

    def run(self, dataframe: pd.DataFrame, output_dir: str | Path = "outputs") -> pd.DataFrame:
        df = self.engineer_features(dataframe)
        if self.target_column not in df:
            raise ValueError(f"Target column not found: {self.target_column}")

        groups = self._groups(df)
        all_features = groups["base"]
        scenarios = {
            "all_features": all_features,
            "without_network_features": [c for c in all_features if c not in groups["network"]],
            "without_statistical_features": [c for c in all_features if c not in groups["statistical"]],
            "without_temporal_features": [c for c in all_features if c not in groups["temporal"]],
            "selected_features_only": [c for c in all_features if c in (
                groups["network"] + groups["statistical"] + [
                    "records_affected", "detection_time_hours", "ransom_demand_usd"
                ]
            )],
        }

        X_train, X_test, y_train, y_test = train_test_split(
            df, df[self.target_column], test_size=0.25, random_state=RANDOM_STATE
        )
        rows = []
        for name, columns in scenarios.items():
            columns = [c for c in columns if c in df.columns]
            if not columns:
                continue
            model = self._build_model(X_train[columns])
            model.fit(X_train[columns], y_train)
            pred = model.predict(X_test[columns])
            rows.append({
                "scenario": name,
                "feature_count": len(columns),
                "r2_score": float(r2_score(y_test, pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, pred))),
                "mae": float(mean_absolute_error(y_test, pred)),
            })

        results = pd.DataFrame(rows).sort_values("r2_score", ascending=False).reset_index(drop=True)
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        df.to_csv(out / "engineered_features.csv", index=False)
        results.to_csv(out / "ablation_results.csv", index=False)
        (out / "feature_engineering_report.json").write_text(
            json.dumps({
                "step": 17,
                "target": self.target_column,
                "engineered_feature_count": int(df.shape[1] - 1),
                "scenarios": results.to_dict(orient="records"),
            }, indent=2),
            encoding="utf-8",
        )
        return results


if __name__ == "__main__":
    from src.data_loader import DataLoader
    study = FeatureEngineeringAblationStudy()
    print(study.run(DataLoader().run()).to_string(index=False))
