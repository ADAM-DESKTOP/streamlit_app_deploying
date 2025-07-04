## Prayer App Tracker 🚀

_A beginner-friendly Islamic prayer log built by a passionate first-time developer_

Welcome to my very first web app! 🎉 This tool was created to help users keep track of their daily Islamic prayers, view accurate prayer times based on their location, and privately reflect on their prayer journey. Built using [Streamlit](https://streamlit.io/), SQLite, and Python — so yes, it's lightweight, personal, and very much a labor of learning and love.

**Note:** Since this is my first published project, it may have a few quirks here and there. I'm learning as I go — so if you spot something odd, feel free to drop feedback. It’s all part of the journey!

## ✨ Features

- **Secure Login & Registration**  
    Basic user authentication with a private prayer log for each account
- **Prayer Tracking**  
    Mark each of the five daily prayers as completed — for any date
- **Live Prayer Times**  
    Automatically fetches prayer times based on your IP-based location
- **Calendar View**  
    Go back or forward in time to update or view your prayer history
- **Private Data**  
    Each user’s prayer log is saved in a separate database file just for them

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)

**Installation**

git clone https://github.com/yourusername/prayer-app-tracker.git cd prayer-app-tracker pip install -r requirements.txt streamlit run main.py

🧭 How to Use It

1. **Register an Account**  
    Go to the "Register" tab, enter a username and password, and hit Register.
2. **Login**  
    Use the same credentials to log in.
3. **Track Your Prayers**  
    Select a date and tick off prayers as you complete them — it saves automatically.
4. **See Local Prayer Times**  
    They’ll show up right on the homepage.

🗂 Project Structure

prayer-app-tracker/ │ ├── main.py # Streamlit app entry point ├── database.py # Handles prayer logs ├── prayer_times_calculator.py # Prayer times logic ├── users.txt # Demo-only user storage ├── prayers_.db # User-specific SQLite DBs ├── requirements.txt # Dependencies └── README.md # This file!

🔐 Security Notes

- Passwords are hashed, but this is still a simple demo — don’t use sensitive credentials.
- Each user’s data stays separate. Please don’t share usernames or passwords.

⚙️ Customizing the App

- You can tweak how prayer times are calculated by editing the `get()` function in `main.py`.
- To level up authentication, consider OAuth or a library like `Authlib`.

🪪 License

This project is licensed under the MIT License.

💬 A Personal Note

I built this app as both a faith-based personal tracker and a way to dive into Web Applications development. It’s not perfect, but it’s meaningful — and that makes it worth sharing. 😊

📫 Contact

If you have feedback, ideas, or words of encouragement, feel free to open an issue on GitHub.