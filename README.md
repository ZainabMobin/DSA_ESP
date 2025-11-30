# --------How to download the project---------
[git hub repo link](https://github.com/abdullah6093/Search-Engine-DSA-Project.git)

Version: 1.1


Click Code then Download ZIP
Extract the folder

# --------How to download the dataset----------
Open my google drive link: [google drive link](https://drive.google.com/file/d/1GmIYWho4wU3d7FkseXGNUOiavgDEGk8I/view?usp=drive_link)

Download the dataset that contains around 50k files
Copy the entire dataset folder into the main project folder
The project folder must contain all python files and the dataset in the same place



# -----------How to run the lexicon generator-----------
Open terminal inside the project folder
Run: python lexicon_generator.py
This will create a file named lexicon.txt
This file contains: term, termID, document frequency


# -----------How to run the forward index-----------
Run: python forward_index.py
This will create forward_index.txt
This file contains docID mapped with termIDs and their positions inside the document



# -----------How to run the inverted index-----------

Run: python inverted_index.py
- This will generate inverted_index.txt
- This file contains termID mapped with list of docIDs and positions where the term appears



-----------Final files created-----------

````
lexicon.txt
forward_index.txt
inverted_index.txt
````
# --------How to run using SAMPLE data (CSV file) --------

We have uploaded sample CSV file to GitHub so you can run the project without downloading the full dataset.

Sample files included:

- sample.csv

- lexicon_output.txt

- forward_output.txt

- inverted_output.txt




- Contains Design for pre-built indices
- CORD 2020-4-10 dataset contains 51k+ papers with 59k+ text parses

DONE:

- optimized lexicon, forward index and doc map generator
- contains full generted lexicon in csv format for viewing
- sample generated forward index and doc map files available in csv and json
- optimize inverted index generator
- Upload Dataset (compressed) i.e provide a way to access it with identical folder structure (compatibility with written code)
- Scale system to accomodate dynamic indexing (processing added files, done at runtime)