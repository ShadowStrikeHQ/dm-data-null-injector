import argparse
import logging
import random
import pandas as pd
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Replaces values in a dataset with null values based on probability or pattern matching.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    parser.add_argument("--probability", type=float, default=0.1,
                        help="Probability (0.0 to 1.0) of replacing a value with null. Default is 0.1.")
    parser.add_argument("--pattern", type=str, default=None,
                        help="Regular expression pattern to match values to be replaced with null.  If not specified, all values are considered.")
    parser.add_argument("--columns", type=str, default=None,
                        help="Comma-separated list of column names to apply the null injection to. If not specified, all columns are considered.")
    return parser.parse_args()

def inject_nulls(data: pd.DataFrame, probability: float, pattern: str = None, columns: list = None) -> pd.DataFrame:
    """
    Replaces values in a DataFrame with null values based on the specified probability and pattern.

    Args:
        data (pd.DataFrame): The input DataFrame.
        probability (float): The probability of replacing a value with null (0.0 to 1.0).
        pattern (str, optional): A regular expression pattern to match values. Defaults to None (all values considered).
        columns (list, optional): A list of column names to apply the injection to. Defaults to None (all columns considered).

    Returns:
        pd.DataFrame: The DataFrame with null values injected.

    Raises:
        ValueError: If the probability is not between 0.0 and 1.0.
        TypeError: If the data is not a pandas DataFrame.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")

    if not 0.0 <= probability <= 1.0:
        raise ValueError("Probability must be between 0.0 and 1.0.")

    try:
        cols = data.columns if columns is None else [col.strip() for col in columns]
        for col in cols:
            if col not in data.columns:
                logging.warning(f"Column '{col}' not found. Skipping.")
                continue

            for index, value in data[col].items():
                if pattern is None or (isinstance(value, str) and bool(pd.Series(value).str.match(pattern)[0])):
                    if random.random() < probability:
                        data.at[index, col] = None  # Replace with None (null in pandas)
                        logging.debug(f"Replaced value at index {index}, column '{col}' with None.")
    except Exception as e:
        logging.error(f"An error occurred during null injection: {e}")
        raise

    return data

def main():
    """
    Main function to execute the null injector tool.
    """
    try:
        args = setup_argparse()

        # Input validation
        if not os.path.exists(args.input_file):
            raise FileNotFoundError(f"Input file not found: {args.input_file}")
        
        if not args.input_file.lower().endswith('.csv'):
             raise ValueError("Input file must be a CSV file.")

        # Load data
        try:
             data = pd.read_csv(args.input_file)
        except Exception as e:
            logging.error(f"Failed to read CSV file: {e}")
            raise

        # Prepare column list if specified
        columns = args.columns.split(',') if args.columns else None

        # Inject nulls
        masked_data = inject_nulls(data.copy(), args.probability, args.pattern, columns)

        # Save masked data
        try:
             masked_data.to_csv(args.output_file, index=False)
             logging.info(f"Masked data saved to: {args.output_file}")
        except Exception as e:
             logging.error(f"Failed to write CSV file: {e}")
             raise

    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
    except ValueError as e:
        logging.error(f"Value error: {e}")
    except TypeError as e:
        logging.error(f"Type error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()