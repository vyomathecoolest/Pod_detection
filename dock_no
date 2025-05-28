import cv2
import numpy as np
import easyocr
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
import os


class BatchNineDigitExtractor:
    def __init__(self, debug=False):
        self.debug = debug
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("OCR reader initialized successfully")

    def preprocess_for_digits(self, image_path):
        """Optimized preprocessing specifically for digit recognition"""
        # Load image
        original = cv2.imread(image_path)
        if original is None:
            raise ValueError(f"Could not load image: {image_path}")

        # Convert to grayscale
        if len(original.shape) == 3:
            gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        else:
            gray = original.copy()

        # Enhance contrast for better digit recognition
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Upscale for better OCR (important for small digits)
        height, width = enhanced.shape
        upscaled = cv2.resize(enhanced, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

        # Apply slight Gaussian blur to smooth out noise
        blurred = cv2.GaussianBlur(upscaled, (1, 1), 0)

        # Adaptive thresholding - works well for digits
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        return binary, enhanced, gray

    def extract_nine_digit_numbers(self, image_path):
        """Extract only 9-digit numbers from a single image"""
        try:
            # Preprocess image
            binary, enhanced, gray = self.preprocess_for_digits(image_path)

            # Try OCR on different processed versions
            images_to_try = [
                ("binary", binary),
                ("enhanced", enhanced),
                ("grayscale", gray)
            ]

            nine_digit_numbers = set()  # Use set to avoid duplicates
            confidence_scores = {}  # Store confidence for each number

            for name, img in images_to_try:
                try:
                    # OCR with settings optimized for digits
                    results = self.reader.readtext(img,
                                                   detail=1,
                                                   paragraph=False,
                                                   width_ths=0.8,
                                                   height_ths=0.8)

                    for bbox, text, confidence in results:
                        if confidence > 0.5:  # Higher confidence threshold for digits
                            # Clean the text - remove spaces, special characters
                            cleaned_text = re.sub(r'[^0-9]', '', text)

                            # Look specifically for 9-digit numbers
                            nine_digit_matches = re.findall(r'\d{9}', cleaned_text)

                            # Also check if the entire cleaned text is exactly 9 digits
                            if len(cleaned_text) == 9 and cleaned_text.isdigit():
                                nine_digit_matches.append(cleaned_text)

                            # Add any found 9-digit numbers to our set
                            for match in nine_digit_matches:
                                nine_digit_numbers.add(match)
                                # Keep track of highest confidence for each number
                                if match not in confidence_scores or confidence > confidence_scores[match]:
                                    confidence_scores[match] = confidence

                except Exception as e:
                    if self.debug:
                        print(f"Error processing {name} for {image_path}: {e}")

            # Convert to list and sort
            result_numbers = sorted(list(nine_digit_numbers))
            result_confidences = [confidence_scores.get(num, 0) for num in result_numbers]

            return result_numbers, result_confidences

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return [], []

    def process_folder(self, folder_path, supported_formats=None):
        """Process all images in a folder and extract 9-digit numbers"""
        if supported_formats is None:
            supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

        folder_path = Path(folder_path)
        if not folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # Find all image files
        image_files = []
        for format_ext in supported_formats:
            image_files.extend(folder_path.glob(f"*{format_ext}"))
            image_files.extend(folder_path.glob(f"*{format_ext.upper()}"))

        if not image_files:
            print(f"No image files found in {folder_path}")
            print(f"Supported formats: {supported_formats}")
            return []

        print(f"Found {len(image_files)} image files to process...")

        results = []

        for i, image_file in enumerate(image_files, 1):
            print(f"Processing ({i}/{len(image_files)}): {image_file.name}")

            numbers, confidences = self.extract_nine_digit_numbers(str(image_file))

            if numbers:
                for j, (number, confidence) in enumerate(zip(numbers, confidences)):
                    results.append({
                        'image_file': image_file.name,
                        'image_path': str(image_file),
                        'nine_digit_number': number,
                        'confidence_score': round(confidence, 3),
                        'number_sequence': j + 1,  # If multiple numbers in same image
                        'processing_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                print(f"  → Found {len(numbers)} nine-digit number(s): {', '.join(numbers)}")
            else:
                # Still record the file even if no numbers found
                results.append({
                    'image_file': image_file.name,
                    'image_path': str(image_file),
                    'nine_digit_number': 'Not Found',
                    'confidence_score': 0,
                    'number_sequence': 0,
                    'processing_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"  → No nine-digit numbers found")

        return results

    def save_to_excel(self, results, output_file):
        """Save results to Excel file with formatting"""
        if not results:
            print("No results to save.")
            return

        # Create DataFrame
        df = pd.DataFrame(results)

        # Create summary statistics
        total_images = df['image_file'].nunique()
        images_with_numbers = df[df['nine_digit_number'] != 'Not Found']['image_file'].nunique()
        total_numbers_found = len(df[df['nine_digit_number'] != 'Not Found'])

        summary = {
            'Metric': [
                'Total Images Processed',
                'Images with Numbers Found',
                'Images with No Numbers',
                'Total Nine-Digit Numbers Found',
                'Average Confidence Score'
            ],
            'Value': [
                total_images,
                images_with_numbers,
                total_images - images_with_numbers,
                total_numbers_found,
                round(df[df['nine_digit_number'] != 'Not Found']['confidence_score'].mean(),
                      3) if total_numbers_found > 0 else 0
            ]
        }
        summary_df = pd.DataFrame(summary)

        # Save to Excel with multiple sheets
        output_path = Path(output_file)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main results
            df.to_excel(writer, sheet_name='Results', index=False)

            # Summary statistics
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Numbers only (for easy copying)
            numbers_only = df[df['nine_digit_number'] != 'Not Found'][['image_file', 'nine_digit_number']].copy()
            if not numbers_only.empty:
                numbers_only.to_excel(writer, sheet_name='Numbers_Only', index=False)

        print(f"\nResults saved to: {output_path}")
        print(f"Summary:")
        print(f"  - Total images processed: {total_images}")
        print(f"  - Images with numbers: {images_with_numbers}")
        print(f"  - Total numbers found: {total_numbers_found}")


def process_images_to_excel(folder_path, output_excel_file, debug=False):
    """Main function to process all images in a folder and save to Excel"""

    # Initialize extractor
    extractor = BatchNineDigitExtractor(debug=debug)

    # Process all images in folder
    results = extractor.process_folder(folder_path)

    if results:
        # Save to Excel
        extractor.save_to_excel(results, output_excel_file)

        # Display summary
        df = pd.DataFrame(results)
        found_numbers = df[df['nine_digit_number'] != 'Not Found']

        if not found_numbers.empty:
            print(f"\n=== FOUND NUMBERS SUMMARY ===")
            for _, row in found_numbers.iterrows():
                print(f"{row['image_file']}: {row['nine_digit_number']} (confidence: {row['confidence_score']})")

        return results
    else:
        print("No images processed successfully.")
        return []


def process_single_image_to_excel(image_path, output_excel_file):
    """Process a single image and save result to Excel"""
    extractor = BatchNineDigitExtractor()

    numbers, confidences = extractor.extract_nine_digit_numbers(image_path)

    results = []
    image_name = Path(image_path).name

    if numbers:
        for i, (number, confidence) in enumerate(zip(numbers, confidences)):
            results.append({
                'image_file': image_name,
                'image_path': image_path,
                'nine_digit_number': number,
                'confidence_score': round(confidence, 3),
                'number_sequence': i + 1,
                'processing_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    else:
        results.append({
            'image_file': image_name,
            'image_path': image_path,
            'nine_digit_number': 'Not Found',
            'confidence_score': 0,
            'number_sequence': 0,
            'processing_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    extractor.save_to_excel(results, output_excel_file)
    return results


# Usage examples
if __name__ == "__main__":

    # Example 1: Process all images in a folder
    folder_path = r"C:\Users\vyoma\OneDrive\Documents\Desktop\internship\classified_by_lsp\GATI"  # Change this to your folder path
    output_file = "extracted_numbers.xlsx"

    print("=== BATCH 9-DIGIT NUMBER EXTRACTOR ===\n")

    try:
        # Method 1: Process entire folder
        results = process_images_to_excel(folder_path, output_file, debug=False)

        # Method 2: Process single image
        # results = process_single_image_to_excel("hello.jpg", "single_image_results.xlsx")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. The folder path exists and contains images")
        print("2. You have pandas and openpyxl installed: pip install pandas openpyxl")
        print("3. The output directory is writable")


# Utility functions for different use cases

def quick_folder_scan(folder_path):
    """Quick scan of folder - just print found numbers without saving"""
    extractor = BatchNineDigitExtractor()
    results = extractor.process_folder(folder_path)

    print("\n=== QUICK SCAN RESULTS ===")
    for result in results:
        if result['nine_digit_number'] != 'Not Found':
            print(f"{result['image_file']}: {result['nine_digit_number']}")


def get_all_numbers_from_folder(folder_path):
    """Return just a list of all found 9-digit numbers"""
    extractor = BatchNineDigitExtractor()
    results = extractor.process_folder(folder_path)

    numbers = [r['nine_digit_number'] for r in results if r['nine_digit_number'] != 'Not Found']
    return list(set(numbers))  # Remove duplicates


def create_detailed_report(folder_path, output_file):
    """Create a detailed Excel report with additional analysis"""
    extractor = BatchNineDigitExtractor(debug=True)
    results = extractor.process_folder(folder_path)

    if results:
        df = pd.DataFrame(results)

        # Additional analysis
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main results
            df.to_excel(writer, sheet_name='All_Results', index=False)

            # Only successful extractions
            success_df = df[df['nine_digit_number'] != 'Not Found']
            if not success_df.empty:
                success_df.to_excel(writer, sheet_name='Found_Numbers', index=False)

            # Failed extractions
            failed_df = df[df['nine_digit_number'] == 'Not Found']
            if not failed_df.empty:
                failed_df.to_excel(writer, sheet_name='No_Numbers_Found', index=False)

            # Unique numbers summary
            if not success_df.empty:
                unique_numbers = success_df.drop_duplicates('nine_digit_number')[
                    ['nine_digit_number', 'confidence_score']]
                unique_numbers.to_excel(writer, sheet_name='Unique_Numbers', index=False)

        print(f"Detailed report saved to: {output_file}")
        return results

    return []
