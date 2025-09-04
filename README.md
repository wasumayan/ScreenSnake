# 🐍 ScreenSnake - Birthday Gift Edition! 🎉

A special birthday gift Snake game featuring **Gimmefy** as the default snake, competing against tech giants! 

**Perfect for non-techy users** - just download and double-click to play!

## 🎁 **Birthday Gift Features**

- **Default Theme**: You play as **Gimmefy** (your startup logo) 🚀
- **Tech Rivals**: Compete against Facebook, Jasper, OpenAI, Netflix, and Instagram
- **Classic Mode**: Switch to the original tiger-striped snake vs college rivals
- **Princeton Food**: Always represented by the Princeton logo 🎓

## 🚀 **Quick Start (For Non-Techy Users)**

### **Option 1: Download Ready-to-Run App (Recommended)**

1. **Download the game**: Click the green "Code" button above, then "Download ZIP"
2. **Extract the ZIP**: Right-click the downloaded file and choose "Extract All"
3. **Run the game**: Double-click `screen_snake.py` (or the `.app` file if available)

### **Option 2: Run from Source (For Tech-Savvy Users)**

1. **Clone the repo:**
   ```sh
   git clone https://github.com/wasumayan/ScreenSnake.git
   cd ScreenSnake
   ```

2. **Set up Python environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install PyQt5
   ```

4. **Run the game:**
   ```sh
   python screen_snake.py
   ```

## 🎮 **How to Play**

### **Controls:**
- **Arrow keys**: Move your snake
- **P**: Pause/Unpause
- **1**: Gimmefy theme (default - tech companies as rivals)
- **2**: Original theme (tiger snake vs college rivals)
- **Space**: Restart after game over
- **ESC or Mouse Click**: Quit

### **Theme Switching:**
1. **Press P** to pause
2. **Press 1** for Gimmefy theme (default)
3. **Press 2** for original college theme
4. **Press P again** to unpause

## 🎯 **Game Features**

- **Gimmefy as your snake** (default) - your startup logo!
- **Tech company rivals**: FB, Jasper, OpenAI, Netflix, IG
- **Princeton logo** as food
- **Score tracking** with high scores
- **Dynamic speed** that increases as you score
- **AI difficulty** that gets smarter over time
- **Full-screen transparent overlay**
- **Snake wraps around screen edges**

## 🖥️ **System Requirements**

- **macOS**: 10.14+ (Mojave or later)
- **Windows**: Windows 10 or later
- **Python**: 3.7+ (if running from source)
- **Memory**: 100MB RAM
- **Storage**: 50MB free space

## 📱 **macOS App Distribution**

If you want a standalone `.app` for macOS:

```sh
pip install pyinstaller
pyinstaller --windowed --add-data "*.png:." --add-data "high_scores.json:." --icon screensnake.icns screen_snake.py
```

The `.app` will be in the `dist/` folder.

**Note:** macOS may warn about unidentified developers. Right-click the app and choose "Open" to bypass.

## 🆘 **Troubleshooting**

### **Common Issues:**

- **"App can't be opened"**: Right-click → Open → Open
- **Missing images**: Make sure all `.png` files are in the same folder
- **Game won't start**: Try running from terminal first to see error messages

### **For Non-Techy Users:**
- **Ask a tech-savvy friend** to help with setup
- **Use the ready-to-run app** if available
- **Check the "Issues" tab** on GitHub for help

## 🎉 **Birthday Gift Instructions**

**For the Birthday Person:**
1. Download and extract the ZIP file
2. Double-click `screen_snake.py` to start
3. You'll immediately see **Gimmefy** as your snake!
4. Compete against tech giants (FB, Jasper, OpenAI, etc.)
5. Press P to pause and switch themes if you want

## 📁 **Files Included**

- `screen_snake.py` - Main game file
- `gimmefy_icon.png` - Your startup logo (the snake!)
- `fb_icon.png`, `jasper_icon.png`, etc. - Tech company rivals
- `princeton_logo.png` - Food icon
- `high_scores.json` - High score storage

## 🤝 **Support**

- **GitHub Issues**: Report problems or ask questions
- **For non-techy users**: Ask a tech-savvy friend for help
- **Email**: Contact the developer for direct support

## 🎊 **Happy Birthday!**

Enjoy playing as Gimmefy and competing against the tech giants! 

**Made with ❤️ as a birthday gift**

---

**Repository**: [https://github.com/wasumayan/ScreenSnake](https://github.com/wasumayan/ScreenSnake) 