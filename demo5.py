import requests
import nbformat
import ast
from langchain_ollama import OllamaLLM

# GitHub API URL'si
username = 'kosor8'  # GitHub kullanıcı adınızı yazın
repo_name = 'chatbot'  # Repo adınızı yazın
url = f'https://api.github.com/repos/{username}/{repo_name}/contents/'  # Repo içeriklerine erişim

# Ollama modelini başlat
llm = OllamaLLM(model="llama3")

# GitHub reposundaki .ipynb dosyalarını çekme
response = requests.get(url)
files = response.json()

# .ipynb dosyalarını ayıklama
notebook_files = [file['download_url'] for file in files if file['name'].endswith('.ipynb')]

# Notebook dosyasını indirme ve analiz etme
def read_notebook(file_url):
    """Notebook'taki soruları ve kodları ayrıştırır."""
    response = requests.get(file_url)
    nb = nbformat.read(response.content, as_version=4)

    questions = []
    codes = []

    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            questions.append(cell['source'])  # Soruların Markdown içeriği
        elif cell.cell_type == 'code':
            codes.append(cell['source'])  # Kod hücreleri

    return questions, codes

def check_syntax(code):
    """Kodun syntax hatası olup olmadığını kontrol eder."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f"Syntax hatası: {str(e)}"

def analyze_code(question, code, cell_num):
    """Syntax ve mantık analizini yapar."""
    syntax_error = check_syntax(code)
    
    if syntax_error:
        return f"Hücre {cell_num}: {syntax_error}"
    
    # LLM ile mantık analizi
    prompt = f"""
    Soru: {question}
    
    Öğrencinin cevabı:
    ```python
    {code}
    ```
    
    Yukarıdaki kod soruya uygun mu? Eğer yanlışsa, öğrencinin yaptığı hatayı açıkla ve nasıl düzeltebileceğini öner.
    """
    response = llm.invoke(prompt)
    
    return f"Hücre {cell_num}: {response}"

def check_homework():
    """Repo'daki her .ipynb dosyasını kontrol eder."""
    for file_url in notebook_files:
        print(f"Kontrol edilen dosya: {file_url}")
        questions, codes = read_notebook(file_url)
        
        for i, (question, code) in enumerate(zip(questions, codes)):
            result = analyze_code(question, code, i + 1)
            print(result)
            print("-" * 50)

if __name__ == "__main__":
    check_homework()
