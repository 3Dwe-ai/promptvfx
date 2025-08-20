## PromptVFX
[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This is an official implementation of **"PromptVFX: Text-Driven Fields for Open-World 3D Gaussian Animation"**. 

## Requirements
- Python 3.7 or higher

## Installation

Install the required packages:

```bash
pip install viser
pip install openai
pip install python-dotenv
```

## Configuration

1. Copy the provided template to create your own environment file:

   ```bash
   cp .env.template .env
   ```

2. Obtain your API key from OpenAI by visiting  
   https://platform.openai.com/account/api-keys

3. Open the newly created `.env` file and add your key:

   ```dotenv
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Run the main script:

```bash
python main.py
```

## License
This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
