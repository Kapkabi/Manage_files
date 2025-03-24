# File Searcher and Organizer

## Description  
A Python application with a graphical user interface for searching files based on specified attributes (extensions) and performing actions on the found files (copying, moving).  

## Features  
- Search for files by specified extensions in the selected directory.  
- Display a list of found files and statistics (count, total size).  
- Logging of search results.  
- Folder selection for processing.  
- Perform actions on files: copy or move them to a specified folder.  
- User-friendly graphical interface using Tkinter.  

## Installation  
1. Clone the repository:  
   ```sh
   git clone https://github.com/Kapkabi/your-repository.git
   cd your-repository
   ```
2. Install dependencies:  
   ```sh
   pip install -r requirements.txt
   ```
   *(Create the `requirements.txt` file if there are dependencies.)*  

## Usage  
1. Select a folder to search for files.  
2. Specify the desired extensions (e.g., `txt`, `jpg`).  
3. Click "Search" and wait for the process to complete.  
4. Select the found files and specify the destination folder.  
5. Choose an action: copy or move.  
6. Click "Execute".  

## Logging  
- Search logs are saved in a file named `log_search_YYYYMMDD_HHMMSS.txt` in the root search folder.  
- Execution logs (`copy` or `move`) are saved in the destination folder.  

## Requirements  
- Python 3.x  
- Tkinter (included in the standard Python library)  

## License  
This project is licensed under the MIT License.  
