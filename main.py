import os
import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox
from tkinter.constants import END
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import ctypes

examples = ["The Great Wall of China, one of the greatest wonders of the world, was built by Qin Shi Huang, the first Emperor of China. It’s a UNESCO World Heritage Site.",
            "Amazon is an American multinational technology company based in Seattle, Washington. It was founded by Jeff Bezos.",
            "Apple Inc., founded by Steve Jobs, Steve Wozniak, and Ronald Wayne, is headquartered in Cupertino, California. They are known for products like the iPhone and Mac computers.",
            "Barack Obama, the former president of the United States, was born in Honolulu, Hawaii. He is a graduate of Harvard Law School.",
            "Microsoft, located in Redmond, Washington, was founded by Bill Gates and Paul Allen. It’s known for creating the Windows operating system.",
            "Tại Mỹ, Cuộc thi Tin học sinh viên do Đại học Khoa học Tự nhiên tổ chức đã diễn ra. Em Nguyễn Văn A là người Việt đã đoạt giải nhất.",
            "Sáng nay, tôi đã đến quán cà phê Góc Phố ở TP.Hồ Chí Minh để gặp ông Trần Anh, CEO của Công ty Công nghệ VinaTech.",
            "Cuộc họp  của Hội đồng Quản trị Đại học Quốc gia Hà Nội sẽ được tổ chức tại Hà Nội với sự tham gia của ông Nguyễn Văn A."]
path = "DISTILBERT-FINE-TUNE/distilbert-base"
path_vn = "DISTILBERT-FINE-TUNE/distilbert-base-multilingual-vn"
model_dir = "model_tokenizer"
current_model = "ENG"
nlp = -1

def create_label(text, color, frame):
    label = tk.Label(frame, text=text, bg=color, fg="white", padx=5, pady=3, font=("Arial", 11, "bold"))
    label.pack(side="left", padx=1)

def display_entities(text, entities):
    result['state'] = 'normal'
    result.delete("1.0", END)
    current_index = 0
    current_label = "O"
    for i, entity in enumerate(entities):
        start_index = entity["start"]
        end_index = entity["end"]
        label = entity["entity"]
        entity_text = text[start_index:end_index]
        pre_token = text[current_index:start_index]
        if(pre_token == " " and label == "I-" + current_label):
            result.insert(END, pre_token, current_label)
        else:
            result.insert(END, pre_token)
        
        current_index = end_index 
        if "PER" in label:
            current_label = "PER"
            result.insert(END, entity_text, "PER")
        elif "LOC" in label:
            current_label = "LOC"
            result.insert(END, entity_text, "LOC")
        elif "ORG" in label:
            current_label = "ORG"
            result.insert(END, entity_text, "ORG")
        else: # "MISC" 
            current_label = "MISC"
            result.insert(END, entity_text, "MISC")
        if len(entities) == i+1:
            result.insert(END, " " + current_label, "END-" + current_label)
        elif "B" in entities[i+1]["entity"]:
            result.insert(END, " " + current_label, "END-" + current_label)
    result.insert(END, text[current_index:])  
    result['state'] = 'disabled'
def send():
    send_text = input_text.get("1.0", "end-1c")
    if send_text.isspace() or send_text == '':
        messagebox.showinfo("Error", "Input cannot be empty or contain only spaces.")
        return
    ner_results = nlp(send_text)
    print(ner_results)
    display_entities(send_text,ner_results)
def read_dir(path):
    all_objects = os.listdir(path)
    checkpoints = [obj for obj in all_objects if "checkpoint-" in obj]
    sorted_checkpoints = sorted(checkpoints, key=lambda x: int(x[11:]))
    return sorted_checkpoints
def on_combobox_select(event):
    global nlp
    global current_model
    selected_item = combobox_epoch.get()
    if 'VN-' in selected_item:
        matches = selected_item[9:]
        number = int(matches) -1
        checkpoint_path = path_vn + "/" + checkpoints_vn[number]
        if(current_model != "VN"):
            current_model = "VN"
            menubutton.config(text="Ví dụ")
            clear_button.config(text="Xóa")
            send_button.config(text="Gửi")
            nlp.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
        nlp.model = AutoModelForTokenClassification.from_pretrained(checkpoint_path)
        
    else:
        matches = selected_item[6:]
        number = int(matches) -1
        checkpoint_path = path + "/" + checkpoints[number]
        if(current_model != "ENG"):
            current_model = "ENG"
            menubutton.config(text="Examples")
            clear_button.config(text="Clear")
            send_button.config(text="Send")
            nlp.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
        nlp.model = AutoModelForTokenClassification.from_pretrained(checkpoint_path)
    input_text.focus_set()
    send_text = input_text.get("1.0", "end-1c")
    if not send_text.isspace() and send_text != '':
        send()

def handle_select(value):
    input_text.delete("1.0", END)
    input_text.insert(END, examples[int(value[:1]) -1])  
    send()
def clear():
    result['state'] = 'normal'
    input_text.delete("1.0", END)
    result.delete("1.0", END)
    result['state'] = 'disabled'
if __name__ == "__main__":
    checkpoints = read_dir(path)
    checkpoints_vn = read_dir(path_vn)
    options = []
    for i in range(len(checkpoints)):
        options.append("Epoch " + str(i + 1))
    for i in range(len(checkpoints_vn)):
        options.append("VN-Epoch " + str(i + 1))
    root = tk.Tk()
    root.iconbitmap('icon.ico')
    bigfont = font.Font(family="Roboto", size=12)
    root.option_add("*TCombobox*Listbox*Font", bigfont)
    root.title("DISTILBERT-BASE-NER")
    root.configure(background="#6eb6fa")
    window_width = 600
    window_height = 630
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - window_width)
    y = (screen_height - window_height) 

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    cmb_frame = ttk.Frame(root)
    cmb_frame.grid(row=0, column=0)

    combobox_epoch = ttk.Combobox(cmb_frame, values=options, font=("Roboto", 12))
    combobox_epoch.grid(row=0, column=0, padx=10, pady=10)
    if(len(options) > 8):
        combobox_epoch.set(options[8])
        tokenizer = AutoTokenizer.from_pretrained(path + "/" + checkpoints[8])
        model = AutoModelForTokenClassification.from_pretrained(path + "/" + checkpoints[8])
        nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    elif(len(options) == 0):
        print(f"Thư mục '{path}' rỗng.")
    else:
        combobox_epoch.set(options[0])
        tokenizer = AutoTokenizer.from_pretrained(path + "/" + checkpoints[0])
        model = AutoModelForTokenClassification.from_pretrained(path + "/" + checkpoints[0])
        nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    combobox_epoch['state'] = 'readonly'
    combobox_epoch.bind("<<ComboboxSelected>>", on_combobox_select)

    btn_frame = ttk.Frame(root)
    btn_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    menubutton = tk.Menubutton(btn_frame, text="Examples", relief="raised", font=bigfont, bg="#3ef769")
    menubutton.pack(side='left', padx=10, fill='both', expand=True)

    clear_button = tk.Button(btn_frame, text = "Clear", relief="raised", font=bigfont, bg='#f5ef38', command= clear)
    clear_button.pack(side='right', padx=10, fill='both')  

    menu = tk.Menu(menubutton, tearoff=False)
    menubutton.configure(menu=menu)

    for index,example in enumerate(examples):
        example = str(index + 1) + ". " + example[:60]
        if len(example) > 60:
            short_option = example[:60] + "..." 
            menu.add_command(label=short_option, command=lambda opt=example: handle_select(opt), font=bigfont)
        else:
            menu.add_command(label=example, command=lambda opt=example: handle_select(opt), font=bigfont)


    input_frame = ttk.Frame(root)
    input_frame.grid(row=2, column=0, padx=10, pady=5)

    input_text = scrolledtext.ScrolledText(input_frame, height=8, width=50, wrap="word")
    input_text.pack(side="left", fill="both")
    input_text.configure(font=("Roboto", 14), spacing1 = 5)

    send_button = tk.Button(root, command=send)
    send_button.config(text='Send', relief="raised", font=bigfont, bg="#e8a74d")
    send_button.grid(row=3, column=0, padx=0, pady=0)

    result_frame = ttk.Frame(root)
    result_frame.grid(row=4, column=0, padx=10, pady=5)
    result = scrolledtext.ScrolledText(result_frame, height=8, width=50, wrap="word")
    result.configure(font=("Roboto", 14), spacing1 = 5, spacing2 = 5)

    result.tag_config("PER", background="red", foreground ="white", font=("Open Sans", 12, "bold") )
    result.tag_config("LOC", background="blue", foreground ="white", font=("Open Sans", 12, "bold") )
    result.tag_config("ORG", background="green", foreground ="white", font=("Open Sans", 12, "bold") )
    result.tag_config("MISC", background="orange", foreground ="white", font=("Open Sans", 12, "bold") )

    result.tag_config("END-PER", background="red", foreground ="white", font=("Roboto", 9, "italic") )
    result.tag_config("END-LOC", background="blue", foreground ="white", font=("Roboto", 9, "italic") )
    result.tag_config("END-ORG", background="green", foreground ="white", font=("Roboto", 9, "italic") )
    result.tag_config("END-MISC", background="orange", foreground ="white", font=("Roboto", 9, "italic") )
    result.pack()
    result['state'] = 'disabled'

    label_frame = ttk.Frame(root)
    label_frame.grid(row=6, column=0)
    create_label("PER (Person)", "red", label_frame)
    create_label("LOC (Location)", "blue", label_frame)
    create_label("ORG (Organization)", "green", label_frame)
    create_label("MISC (Miscellaneous)", "orange", label_frame)
    
    root.mainloop()