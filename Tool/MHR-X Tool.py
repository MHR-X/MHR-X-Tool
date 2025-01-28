import requests
import os
import pyfiglet
import whois
from colorama import init, Fore, Style
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from tqdm import tqdm
import signal

# تفعيل colorama
init(autoreset=True)

# دالة لعرض اللوجو بشكل مميز
def show_logo():
    logo = pyfiglet.figlet_format("MHR-X", font="slant")  # استخدام خط كبير
    print(Fore.YELLOW + Style.BRIGHT + logo)  # طباعة اللوجو بلون أصفر
    print(Fore.GREEN + "By Mohamed Heroo\n")
    print(Fore.CYAN + "="*40)
    print(Fore.MAGENTA + "Collecting data, testing files, and more...\n")

# دالة لجمع بيانات عن الموقع
def gather_data(url):
    print(f"\n{Fore.CYAN}Gathering Site Data for {url}:\n")
    
    # جلب معلومات WHOIS
    domain = url.split("//")[-1].split("/")[0]
    try:
        w = whois.whois(domain)
        print(f"{Fore.GREEN}Creation Date: {w.creation_date if w.creation_date else 'N/A'}")
        print(f"{Fore.GREEN}Registrar: {w.registrar}")
        print(f"{Fore.GREEN}Country: {w.country}\n")
    except Exception as e:
        print(f"{Fore.RED}Error retrieving WHOIS data: {e}")

    # جلب معلومات أخرى مثل حجم المحتوى
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"{Fore.GREEN}Status Code: {response.status_code}")
            print(f"{Fore.GREEN}Content Length: {len(response.content)} bytes\n")
            
            # تحليل HTML للحصول على اللغات والتقنيات المستخدمة
            soup = BeautifulSoup(response.text, "html.parser")
            techs = set()  # لتخزين اللغات والتقنيات الفريدة
            
            if soup.find("script", {"src": True}):
                techs.add("JavaScript")
            if soup.find("link", {"rel": "stylesheet"}):
                techs.add("CSS")
            if "PHP" in response.text:
                techs.add("PHP")
            if "Python" in response.text:
                techs.add("Python")
            
            if techs:
                print(f"{Fore.GREEN}Technologies Used: {', '.join(techs)}")
            else:
                print(f"{Fore.RED}No clear technologies detected.")
        else:
            print(f"{Fore.RED}Failed to retrieve data. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error occurred while retrieving site content: {e}\n")

# دالة لاختبار كلمات من "Wordlist"
def test_wordlist(url, wordlist):
    print(f"\n{Fore.CYAN}Testing Wordlist on {url}:\n")
    
    found_urls = []
    not_found_urls = []
    
    stop = False
    lock = False  # To handle if the user stops the process

    # دالة لاختبار كل كلمة من wordlist
    def check_word(word):
        nonlocal stop
        if stop:
            return None, None
        test_url = f"{url}/{word}"
        try:
            # إضافة بعض headers لتقليل الحجم المرسل من الخادم
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            response = requests.get(test_url, headers=headers, timeout=3)  # تحديد timeout أقل لتسريع العملية
            if response.status_code == 200:
                found_urls.append(test_url)
                return (test_url, True)
            else:
                not_found_urls.append(test_url)
                return (test_url, False)
        except requests.exceptions.RequestException:
            not_found_urls.append(test_url)
            return (test_url, False)

    # دالة لإيقاف البحث
    def signal_handler(sig, frame):
        nonlocal stop
        stop = True
        print(f"\n{Fore.YELLOW}Search stopped by user. Showing current results...\n")
    
    # ربط الإشارة لإيقاف البحث
    signal.signal(signal.SIGINT, signal_handler)

    # استخدام tqdm لشريط تحميل خلال الفحص
    with tqdm(total=len(wordlist), desc="Testing words", ncols=100) as pbar:
        with ThreadPoolExecutor(max_workers=50) as executor:  # زيادة عدد الخيوط لتسريع العملية
            futures = [executor.submit(check_word, word) for word in wordlist]
            
            # متابعة تقدم شريط التحميل
            for future in as_completed(futures):
                if stop:
                    break
                test_url, is_found = future.result()
                if test_url is None:
                    break
                if is_found:
                    pbar.set_postfix({"Status": "Found"})
                else:
                    pbar.set_postfix({"Status": "Not Found"})
                pbar.update(1)

    # عرض نتائج الفحص
    print(f"\n{Fore.GREEN}Words Found: {len(found_urls)}")
    print(f"{Fore.RED}Words Not Found: {len(not_found_urls)}\n")
    
    if found_urls:
        print(f"\n{Fore.GREEN}Found URLs: ")
        for url in found_urls:
            print(Fore.GREEN + url)  # الطباعة باللون الأخضر
    
    if not_found_urls:
        print(f"\n{Fore.RED}Not Found URLs: ")
        for url in not_found_urls:
            print(Fore.RED + url)  # الطباعة باللون الأحمر

# دالة لعرض معلومات عن الأداة
# دالة لعرض معلومات عن الأداة
def about():
    print(f"\n{Fore.CYAN}MHR-X Tool\n")
    print(f"{Fore.GREEN}Version: 1.0")
    print(f"{Fore.GREEN}Created by: Mohamed Heroo\n")
    
    print(f"{Fore.MAGENTA}This tool helps you gather site data and find custom files.\n")
    
    print(f"{Fore.YELLOW}How the Tool Works:\n")
    print(f"{Fore.GREEN}1. Gather Site Data:")
    print(f"{Fore.YELLOW}   - When you provide a URL, the tool extracts important information about the site such as WHOIS data, creation date, and country of registration.")
    print(f"{Fore.YELLOW}   - The tool also analyzes the content of the site and attempts to detect the technologies used, like PHP, Python, JavaScript, etc.")
    print(f"{Fore.GREEN}2. Test Wordlist:")
    print(f"{Fore.YELLOW}   - The tool allows you to test a wordlist on a given site URL.")
    print(f"{Fore.YELLOW}   - The wordlist is a collection of possible file or path names. The tool will attempt to access each word in the list by appending it to the given URL.")
    print(f"{Fore.YELLOW}   - Example: If the URL is 'http://example.com' and the wordlist contains 'admin', the tool will test 'http://example.com/admin'.")
    print(f"{Fore.YELLOW}   - The tool checks the status code of each attempt to see if the file or path exists (status code 200).")
    
    print(f"{Fore.RED}Important Notes:")
    print(f"{Fore.YELLOW}   - Make sure you enter the URL without the trailing slash ('/') at the end of the URL.")
    print(f"{Fore.YELLOW}   - For example, use 'http://example.com' instead of 'http://example.com/' to avoid errors.")
    
    print(f"{Fore.YELLOW}3. Error Handling:")
    print(f"{Fore.YELLOW}   - If the site is unreachable or any error occurs during the process, the tool will notify you with an error message.")
    print(f"{Fore.YELLOW}   - The tool also stops the process if you press 'Ctrl+C' or if the user manually stops the search.")
    
    print(f"\n{Fore.GREEN}This tool is designed to help security researchers, penetration testers, and web administrators gather site information and test potential vulnerabilities using wordlist attacks.")
    print(f"{Fore.YELLOW}Use responsibly and only on websites you have permission to test.\n")

# الدالة الرئيسية للتفاعل مع المستخدم
def main():
    show_logo()

    while True:
        print(Fore.YELLOW + "Select an option:")
        print(Fore.CYAN + "1. Gather Site Data")
        print(Fore.CYAN + "2. Test Wordlist")
        print(Fore.CYAN + "3. About")
        print(Fore.RED + "4. Exit")
        
        choice = input(Fore.GREEN + "\nEnter your choice (1/2/3/4): ").strip()

        if choice == '1':
            url = input(Fore.GREEN + "\nEnter the site URL: ").strip()
            gather_data(url)
        elif choice == '2':
            url = input(Fore.GREEN + "\nEnter the site URL: ").strip()
            wordlist_file = input(Fore.GREEN + "\nEnter the path to the wordlist file: ").strip()
            
            # قراءة الكلمات من الملف
            with open(wordlist_file, "r") as file:
                wordlist = [line.strip() for line in file.readlines()]
            
            test_wordlist(url, wordlist)
        elif choice == '3':
            about()
        elif choice == '4':
            print(Fore.RED + "\nExiting the tool. Goodbye!")
            break
        else:
            print(Fore.RED + "\nInvalid choice. Please select again.\n")

if __name__ == "__main__":
    main()
