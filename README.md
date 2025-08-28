# QuickPickHR - CSV Data Analysis with AI Chat

A Django web application that allows users to upload CSV files, automatically rank and sort the data, and interact with the data using AI-powered chat through Ollama.

## Features

- **CSV Upload & Processing**: Upload CSV files and automatically rank data based on numeric columns
- **Data Visualization**: View top-ranked records in a clean, sortable table
- **AI-Powered Chat**: Ask questions about your data using local Ollama AI models
- **Data Management**: View, delete, and manage multiple CSV uploads
- **Responsive Design**: Modern Bootstrap-based UI that works on all devices

## Installation & Setup

### Prerequisites
- Python 3.8+
- Ollama (for AI chat functionality)

### Installation Steps

1. **Clone and Setup Environment**
   ```bash
   cd /path/to/your/project
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install Django>=4.2 pandas requests python-multipart
   ```

3. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Setup Ollama (for AI Chat)**
   - Download and install Ollama from [ollama.ai](https://ollama.ai)
   - Pull a model: `ollama pull llama2`
   - Start Ollama service: `ollama serve`

## Usage

1. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

2. **Access the Application**
   - Open your browser to `http://localhost:8000`
   - Upload a CSV file using the upload form
   - View ranked data and chat with your data

3. **Sample Data**
   - A sample CSV file `sample_employees.csv` is included for testing
   - Contains employee data with various metrics for ranking

## How It Works

### Data Processing
1. **Upload**: Users upload CSV files through the web interface
2. **Analysis**: The system analyzes numeric columns to calculate scores
3. **Ranking**: Records are automatically ranked based on calculated scores
4. **Storage**: Data is stored in Django models for quick access

### Scoring Algorithm
- If one numeric column exists: uses that column directly
- If multiple numeric columns exist: normalizes and sums all numeric values
- If no numeric columns exist: assigns random scores for demonstration

### AI Chat Integration
- Uses local Ollama installation for privacy and control
- Provides context about top-ranked records to the AI
- Supports natural language queries about the data
- Chat history is maintained per upload session

## Project Structure

```
quickpickhr/
├── core/                    # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin interface
│   ├── templates/          # HTML templates
│   └── templatetags/       # Custom template filters
├── quickpickhr/            # Django project settings
├── media/                  # Uploaded files
├── static/                 # Static assets
├── sample_employees.csv    # Sample data for testing
└── manage.py              # Django management script
```

## Models

- **CSVUpload**: Stores uploaded file information
- **CSVRecord**: Individual data records with rankings
- **ChatSession**: Chat sessions per upload
- **ChatMessage**: Individual chat messages

## API Endpoints

- `/`: Home page with upload form
- `/upload/`: Handle CSV file uploads
- `/data/<id>/`: View ranked data
- `/chat/<id>/`: Chat interface
- `/api/send-message/<id>/`: AJAX endpoint for chat messages
- `/delete/<id>/`: Delete uploaded data

## Configuration

### Ollama Models
Edit the model name in `core/views.py` in the `query_ollama` function:
```python
payload = {
    "model": "llama2",  # Change to your preferred model
    # ...
}
```

### File Upload Limits
Modify in `settings.py`:
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if the model is available: `ollama list`
- Verify the model name in the code matches your installed model

### CSV Processing Issues
- Ensure CSV files have proper headers
- Check for encoding issues (UTF-8 recommended)
- Verify numeric columns contain valid numbers

### Media Files Not Serving
- Check `MEDIA_ROOT` and `MEDIA_URL` settings
- Ensure media directory exists and is writable

## Development

### Adding New Features
1. Update models in `core/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Update views and templates as needed

### Testing
- Upload the provided `sample_employees.csv` for testing
- Test chat functionality with questions like:
  - "Who are the top 5 performers?"
  - "What patterns do you see in the data?"
  - "Summarize the key insights"

## License

This project is created for educational and demonstration purposes.

## Support

For issues and questions, please check the Django and Ollama documentation:
- [Django Documentation](https://docs.djangoproject.com/)
- [Ollama Documentation](https://ollama.ai/docs)
