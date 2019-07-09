import os

col_names = ["product/productId", "review/userId", "review/profileName", "review/helpfulness",
             "review/score", "review/time", "review/summary", "review/text"]

data_file_path = os.path.normpath(os.path.join(os.getcwd(), "foods.txt"))

review_text_col_name = "review/text"
summary_text_col_name = "review/summary"
