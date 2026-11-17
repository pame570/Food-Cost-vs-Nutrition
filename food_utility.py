"""
food_utility.py
Utility functions for the Food Cost vs. Nutrition Trade-off Project.
This module keeps the notebook clean by handling data loading, cleaning, and feature engineering.
"""

import pandas as pd
import numpy as np

#----------------------------------------
# MenuStat-related functions
#----------------------------------------

def load_menustat(path: str) -> pd.DataFrame:
    """
    Loading the DOHMH MenuStat CSV file into a pandas DataFrame.
    """
    df = pd.read_csv(
        path,
        low_memory=False
    )
    return df

def clean_menustat(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: drop items missing calories, protein, or fiber and keep needed columns."""
    keep_cols = [
        "restaurant", "Food_Category", "Item_Name", "Calories",
        "Total_Fat", "Saturated_Fat", "Sodium", "Dietary_Fiber",
        "Carbohydrates", "Protein", "Sugar"
    ]
    df = df.loc[df["Calories"].notna(), keep_cols].copy()

    # Drop rows missing key NDD nutrients
    key_cols = ["Calories", "Protein", "Dietary_Fiber"]
    df = df.dropna(subset=key_cols)
    
    df["Food_Category"] = df["Food_Category"].str.strip()
    return df

#------------------------------------------------------------------------
# Category Mapping: MenuStat food category and FMAP EFPG Name(food group)
#------------------------------------------------------------------------

category_map = {
    "Beverages": "Beverages",
    "Sandwiches": "Grains",
    "Salads": "Vegetables",
    "Soup": "Prepared Foods",
    "Burgers": "Meat",
    "Entrees": "Prepared Foods",
    "Appetizers & Sides": "Prepared Foods",
    "Fried Potatoes": "Vegetables",
    "Toppings & Ingredients": "Other Foods",
    "Desserts": "Sugars & Sweets",
    "Baked Goods": "Grains",
    "Pizza": "Grains"
}

def category_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """ 
    Applying the EFPG mapping to MenuStat categories to align
    with USDA F-MAP food groups.
    """
    df = df.copy()
    df["Food_Group"] = df["Food_Category"].map(category_map)
    return df

#-----------------------------------------
# F-MAP price related functions
#-----------------------------------------

def load_fmap(path: str, sheet_name: str | int = 0) -> pd.DataFrame:
    """Loading the USDA F-MAP Excel file."""
    df = pd.read_excel(path, sheet_name=sheet_name)
    return df

def clean_fmap_years(
    df: pd.DataFrame,
    year_col: str,
    start_year: int = 2017,
    end_year: int = 2018,
) -> pd.DataFrame:
    """
    Filter the F-MAP data to a year range (default 2017-2018).
    """
    mask_year = (df[year_col] >= start_year) & (df[year_col] <= end_year)
    df_years = df.loc[mask_year].copy()
    return df_years

def average_price_by_group(
    df: pd.DataFrame,
    food_group_col: str,
    price_col: str,
    area_col: str | None = None,
) -> pd.DataFrame:
    """ To compute the average price per food group.
    To also average over areas as well if needed.
    """
    group_cols = [food_group_col]
    if area_col is not None:
        group_cols.append(area_col)

    grouped = (
        df.groupby(group_cols, as_index=False)[price_col]
        .mean()
    )
    if area_col is not None:
        grouped = (
            grouped.groupby(food_group_col, as_index=False)[price_col]
            .mean()
        )

    out = grouped.rename(columns={
        food_group_col: "Food_Group",
        price_col: "Avg_Price",
    })
    return out

def fmap_category_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """
    To map detailed EFPG_name groups in F-MAP to broad Food_Group labels
    that are comparable to MenuStat (Beverages, Grains, Vegetables, etc.).
    """
    def classify(name: str) -> str:
        n = str(name).lower()

        # Beverages
        if ("juice" in n or "soft drink" in n or "beverage" in n or
            "coffee" in n or "tea" in n or "milk" in n or "alcohol" in n):
            return "Beverages"

        # Grains (breads, cereal, rice, pasta, flour, tortillas)
        if ("bread" in n or "cereal" in n or "grain" in n or "rice" in n or
            "pasta" in n or "flour" in n or "tortilla" in n or "noodle" in n):
            return "Grains"

        # Vegetables & potatoes & legumes
        if ("vegetable" in n or "potato" in n or "tomato" in n or
            "salad" in n or "legume" in n or "bean" in n):
            return "Vegetables"

        # Meat / protein foods
        if ("meat" in n or "beef" in n or "pork" in n or "chicken" in n or
            "turkey" in n or "fish" in n or "seafood" in n or "egg" in n):
            return "Meat"

        # Sugars & sweets
        if ("dessert" in n or "sweet" in n or "sugar" in n or "candy" in n or
            "ice cream" in n or "cake" in n or "cookie" in n or "pie" in n):
            return "Sugars & Sweets"

        # Default for mixed items
        return "Prepared Foods"

    out = df.copy()
    out["Food_Group"] = out["EFPG_name"].apply(classify)
    return out

#------------------------------------------
# Table 8 (nutrition guideline) functions
#------------------------------------------

def load_table8(path: str, sheet_name: str | int = 0) -> pd.DataFrame:
    """Loading USDA Table 8 Recommended Nutrient Density."""
    df = pd.read_excel(path, sheet_name=sheet_name)
    return df

def clean_table8(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converting the Table 8 sheet into a tidy table with:
         Food_Group: short label for the nutrient/food group
         rec_per_1000kcal: recommended density per 1,000 kcal
    """
    # Keeping only the body rows that contain actual data necessary for my project
    body = df.iloc[3:].copy()         

    # First column is the nutrient/food group name, second is the recommended value
    body = body.rename(columns={
        body.columns[0]: "Food_Group_raw",
        body.columns[1]: "rec_per_1000kcal",
    })

    # Dropping rows where the recommended density is missing
    body = body.dropna(subset=["rec_per_1000kcal"])

    # Creating a shorter Food_Group label that can be mapped to the categories
    body["Food_Group"] = (
        body["Food_Group_raw"]
        .astype(str)
        .str.replace(r"\s*\(.*\)", "", regex=True)  # to remove units in parentheses
        .str.strip()
    )

    return body[["Food_Group", "rec_per_1000kcal"]]

RELEVANT_T8_GROUPS = ["Total vegetables", "Fruits", "Grains", "Dairy", "Protein foods"]

FOOD_GROUP_T8_MAP = {
    "Vegetables": "Total vegetables",
    "Fruits": "Fruits",
    "Grains": "Grains",
    "Dairy": "Dairy",
    "Meat": "Protein foods",
}

def make_table8_subset(table8_df):
    return table8_df[table8_df["Food_Group"].isin(RELEVANT_T8_GROUPS)].copy()

def add_food_group_t8(final_df):
    out = final_df.copy()
    out["Food_Group_t8"] = out["Food_Group"].map(FOOD_GROUP_T8_MAP)
    return out

def build_table8_compare(final_df, table8_df):
    t8_subset = make_table8_subset(table8_df)
    df = add_food_group_t8(final_df)

    # comparing fiber only, in grams per 1000 kcal.
    # This function assumes Table 8 rec_per_1000kcal values are fiber recommendations for each mapped food group.
    comparison_df = (
    df.dropna(subset=["Food_Group_t8", "Dietary_Fiber_per_100kcal"])
      .assign(
          actual_per_1000kcal=lambda d: d["Dietary_Fiber_per_100kcal"] * 10
      )
      .groupby("Food_Group_t8", as_index=False)["actual_per_1000kcal"]
      .mean()
    )
    
    table8_compare = comparison_df.merge(
        t8_subset[["Food_Group", "rec_per_1000kcal"]],
        left_on="Food_Group_t8",
        right_on="Food_Group",
        how="left",
    )
    return table8_compare


def merge_with_table8(df: pd.DataFrame, table8_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge Table 8 recommended nutrient density benchmarks onto the analysis dataframe.
    """
    out = df.copy()
    out["Food_Group"] = out["Food_Group"].astype(str).str.strip()
    t8 = table8_df.copy()
    t8["Food_Group"] = t8["Food_Group"].astype(str).str.strip()

    return out.merge(t8, on="Food_Group", how="left")


#-------------------------------------------------------------
# Nutrient Density and Nutrient Density per Dollar (NDD) Score
#-------------------------------------------------------------

def nutrient_density(menu_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute nutrient density per 100 kcal for each item.
    Creates columns like Protein_per_100kcal, Fiber_per_100kcal, etc.
    """
    df = menu_df.copy()
    for col in ["Protein", "Dietary_Fiber", "Sugar", "Sodium"]:
        if col in df.columns:
            df[f"{col}_per_100kcal"] = df[col] / df["Calories"] * 100
    return df

def merge_with_price(nd_df: pd.DataFrame, fmap_df: pd.DataFrame) -> pd.DataFrame:
    """ Merging nutrient-density data with price by Food_Group."""
    merged = nd_df.merge(fmap_df, on="Food_Group", how="inner")
    return merged

def compute_ndd(merged_df: pd.DataFrame) -> pd.DataFrame: # currently uses protein and fiber only
    """
    Compute Nutrient Density per Dollar (NDD) for each item.
    NDD = (Protein_per_100kcal + Dietary_Fiber_per_100kcal) / Avg_Price
    """
    df = merged_df.copy()
    nutrient_cols = ["Protein_per_100kcal", "Dietary_Fiber_per_100kcal"]
    df["nutrient_index"] = df[nutrient_cols].sum(axis=1)
    
    #To avoid division by zero, setting zero/negative prices to NaN
    df.loc[df["Avg_Price"] <= 0, "Avg_Price"] = np.nan
    
    # Applying the Avg_price column coming from F-MAP
    df["NDD"] = df["nutrient_index"] / df["Avg_Price"]
    return df
