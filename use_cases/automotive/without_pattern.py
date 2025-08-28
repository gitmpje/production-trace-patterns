import glob
import json
import os
import zipfile

from pandas import DataFrame, isna
from time import time

DATA_DIR = "data"


# Function to load dataset
def load_zip_json_to_df(data_dir: str) -> DataFrame:
    records = []
    zip_files = [f for f in glob.glob(os.path.join(data_dir, "*.zip"))]
    for zip_path in zip_files:
        zip_name = os.path.basename(zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for file_name in zip_ref.namelist():
                with zip_ref.open(file_name) as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        for obj in content:
                            obj["zip_file"] = zip_name
                            records.append(obj)
                    else:
                        content["zip_file"] = zip_name
                        records.append(content)
    df = DataFrame(records)

    return df


# 1) Number of times a machine state switches during processing of an order.
def use_case_1(order_id: str) -> list:
    results = []
    df_order = df[mask_orders & (df["id"] == order_id)]
    for resource_id in df_order["allocatedId"]:
        t_track_in = df_order[
            (df_order["allocatedId"] == resource_id) & isna(df_order["finished"])
        ]["lastUpdated"].iloc[0]
        t_track_out = df_order[
            (df_order["allocatedId"] == resource_id) & ~isna(df_order["finished"])
        ]["lastUpdated"].iloc[0]

        results.append(
            {
                "Resource": resource_id,
                "ProductionEntity": order_id,
                "intervalStartTime": t_track_in,
                "intervalEndTime": t_track_out,
                "eventCount": sum(
                    (df["id"] == resource_id)
                    & (df["lastUpdated"] >= t_track_in)
                    & (df["lastUpdated"] <= t_track_out)
                ),
            }
        )
    return DataFrame(results)


# 2) List all states of a machine during processing of an order.
def use_case_2(order_id: str) -> list:
    results = []
    df_order = df[mask_orders & (df["id"] == order_id)]
    for resource_id in df_order["allocatedId"]:
        t_track_in = df_order[
            (df_order["allocatedId"] == resource_id) & isna(df_order["finished"])
        ]["lastUpdated"].iloc[0]
        t_track_out = df_order[
            (df_order["allocatedId"] == resource_id) & ~isna(df_order["finished"])
        ]["lastUpdated"].iloc[0]
        results.append(
            {
                "Resource": resource_id,
                "ProductionEntity": order_id,
                "intervalStartTime": t_track_in,
                "intervalEndTime": t_track_out,
                "groupConcat": ", ".join(
                    df[
                        (df["id"] == resource_id)
                        & (df["lastUpdated"] >= t_track_in)
                        & (df["lastUpdated"] <= t_track_out)
                    ]["state"].values
                ),
            }
        )
    return DataFrame(results)


# 3) Time between processing orders on a machine.
def use_case_3(resource_id: str) -> list:
    results = []
    df_resource_allocated = df[df["allocatedId"] == resource_id]
    for record in df_resource_allocated[isna(df_resource_allocated["finished"])][
        ["id", "lastUpdated"]
    ].values:
        t_track_in = df_resource_allocated[(df_resource_allocated["id"] == record[0])][
            "lastUpdated"
        ].iloc[0]
        t_prec_track_out = df_resource_allocated[
            ~isna(df_resource_allocated["finished"])
            & (df_resource_allocated["lastUpdated"] < t_track_in)
        ]["lastUpdated"].max()

        results.append(
            {
                "Resource": resource_id,
                "Event": f"{record[0]}_{record[1]}",
                "elapsedTime": t_track_in - t_prec_track_out,
            }
        )
    df_results = DataFrame(results)
    return df_results[df_results["elapsedTime"] != 0].sort_values("elapsedTime")


# 4.1) Time a machine is in a state.
def use_case_4_1(resource_id: str) -> list:
    df_resource_sorted = (
        df[df["id"] == resource_id][["id", "lastUpdated", "state"]]
        .sort_values("lastUpdated")
        .copy()
    )
    df_resource_sorted["elapsedTime"] = (
        df_resource_sorted["lastUpdated"].shift(-1) - df_resource_sorted["lastUpdated"]
    )

    df_resource_sorted["Event"] = (
        df_resource_sorted["id"] + "_" + df_resource_sorted["lastUpdated"].astype(str)
    )
    df_resource_sorted["Resource"] = df_resource_sorted["id"]
    df_resource_sorted["value"] = df_resource_sorted["state"]
    return df_resource_sorted[df_resource_sorted["elapsedTime"] != 0][
        ["Resource", "Event", "value", "elapsedTime"]
    ].sort_values("elapsedTime")


# 4.2) Time between observing products at a Work Station.
def use_case_4_2(station_id: str) -> list:
    df_at_station_sorted = (
        df[df["locationEntityId"] == station_id][
            ["locationEntityId", "lastUpdated", "id"]
        ]
        .sort_values("lastUpdated")
        .copy()
    )
    df_at_station_sorted["elapsedTime"] = (
        df_at_station_sorted["lastUpdated"].shift(-1)
        - df_at_station_sorted["lastUpdated"]
    )

    df_at_station_sorted["Event"] = (
        df_at_station_sorted["id"]
        + "_"
        + df_at_station_sorted["lastUpdated"].astype(str)
    )
    df_at_station_sorted["Resource"] = df_at_station_sorted["locationEntityId"]
    df_at_station_sorted["value"] = df_at_station_sorted["id"]
    return df_at_station_sorted[df_at_station_sorted["elapsedTime"] != 0][
        ["Resource", "Event", "value", "elapsedTime"]
    ].sort_values("elapsedTime")


# 5) Throughput time per product.
def use_case_5(product_id: str) -> list:
    df_product = df[df["productId"] == product_id]
    t_track_in_min = df_product[isna(df_product["finished"])]["lastUpdated"].min()
    t_track_out_max = df_product[~isna(df_product["finished"])]["lastUpdated"].max()
    return DataFrame(
        [
            {
                "Entity": product_id,
                "elapsedTime": t_track_out_max - t_track_in_min,
            }
        ]
    )


# 6) Relate AGV switch state 'free' event to the product that the AGV was transporting.
def use_case_6(agv_id: str) -> list:
    results = []
    df_agv = df[mask_agvs & (df["id"] == agv_id)]
    for record in df_agv[["id", "lastUpdated"]].values:
        t_event = df_agv[(df_agv["lastUpdated"] < record[1])]["lastUpdated"].max()
        if isna(t_event):
            continue

        content_ids = df_agv[(df_agv["lastUpdated"] == t_event)]["contentIds"].iloc[0]

        if isinstance(content_ids, list) and content_ids:
            results.append(
                {
                    "Event": f"{record[0]}_{record[1]}",
                    "EntityLatest": content_ids[0],
                }
            )
    return DataFrame(results)


# 7) Relate machine level track in events to the corresponding work station.
def use_case_7(resource_id: str) -> list:
    results = []

    # First derive relation between resource (machine) and station
    resource_station = {}
    for record in df[mask_stations].to_dict(orient="records"):
        for child in record["children"]:
            resource_station[child["id"]] = record["id"]

    station_id = resource_station.get(resource_id)
    if station_id:
        for record in df[(df["allocatedId"] == resource_id) & (isna(df["finished"]))][
            ["id", "lastUpdated"]
        ].values:
            results.append(
                {
                    "Event": f"{record[0]}_{record[1]}",
                    "Entity": station_id,
                    "PartEntity": resource_id,
                }
            )
    return DataFrame(results)


# 8) Relate events related to the modules (components) to the product that is composed of those modules.
def use_case_8(product_id: str) -> list:
    results = []

    join_resources = [
        "fbefdec2f0015c2c45d7356f",  # F1_J1
        "9e198cf8cd73b25b153ce27d",  # F1_J2
        "7454c32cca8e5c7e6c9d086e",  # R1_J1
        "8f9e8c99cb96805cbecec2c6",  # R1_J2
    ]

    # Find modules based on description
    product_description = df[df["id"] == product_id]["productDescriptor"].iloc[0]
    module_ids = df[
        mask_modules & df["description"].str.startswith(product_description)
    ]["id"].unique()

    # Find order where modules are joined with product
    order_id = df[
        (df["allocatedId"].isin(join_resources)) & (df["productId"] == product_id)
    ]["id"].iloc[0]

    df_order_track_out = df[(df["id"] == order_id) & (isna(df["finished"]))]
    t_join_track_out = df_order_track_out["lastUpdated"].iloc[0]

    # Iterate over preceding events
    def check_content(x):
        if isinstance(x, list):
            if x:
                return x[0] in module_ids
        return False

    for record in df[
        (
            df["productId"].isin(module_ids)
            | df["id"].isin(module_ids)
            | df["contentIds"].apply(lambda x: check_content(x))
        )
        & (df["lastUpdated"] <= t_join_track_out)
    ][["id", "lastUpdated"]].values:
        results.append(
            {
                "Event": f"{record[0]}_{record[1]}",
                "RelatedProductionEntity": product_id,
            }
        )
    return DataFrame(results)


# 10) Relate orders to the product they are part of.
def use_case_10(product_id: str) -> list:
    results = []
    df_product = df[mask_orders & (df["productId"] == product_id)]
    for resource_id in df_product["allocatedId"].unique():
        df_allocated_resource = df_product[df_product["allocatedId"] == resource_id]
        for t_track_in in df_allocated_resource[
            isna(df_allocated_resource["finished"])
        ]["lastUpdated"].unique():
            t_track_out = df_allocated_resource[
                ~isna(df_allocated_resource["finished"])
                & (df_allocated_resource["lastUpdated"] > t_track_in)
            ]["lastUpdated"].min()

            for order_description in df[
                (df["allocatedId"] == resource_id)
                & (df["lastUpdated"] >= t_track_in)
                & (df["lastUpdated"] <= t_track_out)
            ]["description"].unique():
                results.append(
                    {
                        "PartEntity": df[df["description"] == order_description][
                            "id"
                        ].iloc[0],
                        "ProductionEntity": product_id,
                    }
                )
    return DataFrame(results)


# Execute all and store results as CSV
if __name__ == "__main__":
    df = load_zip_json_to_df(DATA_DIR)

    # Define common DataFrame masks
    global mask_agvs
    mask_agvs = df["zip_file"] == "agvs.zip"
    global mask_modules
    mask_modules = df["zip_file"] == "modules.zip"
    global mask_orders
    mask_orders = df["zip_file"] == "orders.zip"
    global mask_products
    mask_products = df["zip_file"] == "products.zip"
    global mask_resources
    mask_resources = df["zip_file"] == "resources.zip"
    global mask_stations
    mask_stations = df["zip_file"] == "stations.zip"

    with open("pattern_use_cases.json") as f:
        pattern_use_cases = json.load(f)

    for k, d in pattern_use_cases.items():
        start = time()
        df_results = globals()[f"use_case_{k.replace('.', '_')}"](
            d["entity"]["identifier"]
        )
        print(f"Use case {k}: {time() - start} s")
        df_results.drop_duplicates().to_csv(
            f"results/{k}-without_pattern.csv", index=False
        )
