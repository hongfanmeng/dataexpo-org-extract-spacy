# Organization Extractor

## Project Structure

```
.
├── base_config.cfg
├── config.cfg
├── files
│   ├── org_simp.xlsx
│   ├── test_data.xlsx
│   └── words_alpha.txt
├── readme.md
├── requirements.txt
└── src
    ├── config.py
    ├── data
    │   ├── __init__.py
    │   ├── org_list.py
    │   └── website_record.py
    ├── main.py
    ├── nlp
    │   ├── __init__.py
    │   └── org_extractor.py
    ├── prepare_data.py
    ├── test.py
    └── utils.py
```

## Run project

Install requirements

```sh
pip install -r requirements.txt
```

Preparing training data, the script will generate `files/train_40k.spacy` and `files/dev_10k.spacy`

```sh
python src/prepare_data.py
```

Train model

```sh
python -m spacy train config.cfg --output ./models/50k-en --paths.train ./files/train_40k.spacy --paths.dev ./files/dev_10k.spacy --gpu-id 3
```

Test model

```sh
python src/test.py
```

Use own input, replace `files/input.xlsx` with your own input, and run the following, output will be write into `output/output-******.xlsx` (please create output folder before run)

```sh
python src/main.py
```

