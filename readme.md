# Organization Extractor

## Project Structure

```
.
├── config.py
├── data
│   ├── __init__.py
│   ├── org_list.py
│   └── website_record.py
├── files
│   ├── org_simp.xlsx
│   ├── test_data.xlsx
│   └── words_alpha.txt
├── main.py
├── nlp
│   ├── __init__.py
│   └── org_extractor.py
├── prepare_data.py
├── readme.md
├── requirements.txt
└── utils.py
```

## Run project

Install requirements

```sh
pip install -r requirements.txt
```

Preparing training data, the script will generate `files/train_40k.spacy` and `files/dev_10k.spacy`

```sh
python prepare_data.py
```

Train model

```sh
python -m spacy train config.cfg --output ./models/50k-en --paths.train ./files/train_40k.spacy --paths.dev ./files/dev_10k.spacy --gpu-id 3
```

Test model

```sh
python test.py
```

Use own input, replace `files/input.xlsx` with your own input, and run the following, output will be write into `output/output-******.xlsx` (please create output folder before run)

```sh
python main.py
```

