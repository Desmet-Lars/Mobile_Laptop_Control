
# Laptop Control Server

Remote control your Windows laptop through a modern web interface.

## 🚀 Features

- **System Controls**: Shutdown, Restart, Sleep, Hibernate, Lock, Logoff
- **Media Controls**: Play/Pause, Previous, Next track
- **Display**: Brightness control
- **Monitoring**: Real-time CPU, Memory, Battery stats
- **Notifications**: Email alerts on server startup
- **UI**: Dark mode, mobile-responsive design

## 📋 Requirements

- Windows 10/11
- Python 3.7+
- Google account for email notifications

## ⚙️ Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/laptop-control-server.git
   cd laptop-control-server
   ```

2. **Install required packages**
   Install the required Python libraries using:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Set up Google OAuth2**:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Gmail API
   - Download credentials and save as `credentials.json` in the project root
   - The first run will prompt for authentication

2. **Environment Setup**:
   - No additional environment variables are required
   - Logs are automatically created in the `logs/` directory

## Usage

1. **Start the server**:
   Run the server with the following command:
   ```bash
   python app.py
   ```

2. **Access the control panel**:
   Open your browser and navigate to:
   `http://<your-ip>:3000`
   The IP address will be sent via email on startup.

## API Endpoints

- `/` - Main control interface
- `/command` - Execute commands
  **Parameters**:
   - `cmd`: Command to execute
   - `value`: Optional value for commands like brightness

### Available Commands

- `shutdown`
- `restart`
- `sleep`
- `hibernate`
- `lock`
- `logoff`
- `media_play`
- `media_prev`
- `media_next`
- `brightness` (Optional: add a value to adjust brightness)
