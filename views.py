from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import pandas as pd
import json
import requests
import uuid
from .models import CSVUpload, CSVRecord, ChatSession, ChatMessage


def home(request):
    """Home page with upload form and recent uploads"""
    recent_uploads = CSVUpload.objects.all()[:10]
    return render(request, 'core/home.html', {'recent_uploads': recent_uploads})


def upload_csv(request):
    """Handle CSV file upload"""
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'No file selected')
            return redirect('home')
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a CSV file')
            return redirect('home')
        
        # Create CSVUpload instance
        csv_upload = CSVUpload.objects.create(
            name=csv_file.name,
            file=csv_file,
            uploaded_by=request.user if request.user.is_authenticated else None
        )
        
        # Process the CSV file
        try:
            process_csv_file(csv_upload)
            messages.success(request, f'CSV file "{csv_file.name}" uploaded and processed successfully!')
            return redirect('view_data', upload_id=csv_upload.id)
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
            csv_upload.delete()
            return redirect('home')
    
    return redirect('home')


def process_csv_file(csv_upload):
    """Process uploaded CSV file and create records"""
    # Read CSV file
    df = pd.read_csv(csv_upload.file.path)
    
    # Calculate scores based on available numeric columns
    numeric_columns = df.select_dtypes(include=['number']).columns
    
    if len(numeric_columns) > 0:
        # Use first numeric column as primary score, or sum multiple columns
        if len(numeric_columns) == 1:
            df['calculated_score'] = df[numeric_columns[0]]
        else:
            # Normalize and sum multiple numeric columns
            for col in numeric_columns:
                df[col + '_normalized'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            
            score_cols = [col + '_normalized' for col in numeric_columns]
            df['calculated_score'] = df[score_cols].sum(axis=1)
    else:
        # If no numeric columns, assign random scores
        import random
        df['calculated_score'] = [random.uniform(0, 100) for _ in range(len(df))]
    
    # Sort by score (descending)
    df = df.sort_values('calculated_score', ascending=False)
    
    # Create CSVRecord instances
    records = []
    for index, (_, row) in enumerate(df.iterrows()):
        # Convert row to dict, handling NaN values
        row_data = row.to_dict()
        for key, value in row_data.items():
            if pd.isna(value):
                row_data[key] = None
        
        record = CSVRecord(
            csv_upload=csv_upload,
            data=row_data,
            score=float(row_data.get('calculated_score', 0)),
            rank=index + 1
        )
        records.append(record)
    
    # Bulk create records
    CSVRecord.objects.bulk_create(records)
    
    # Mark as processed
    csv_upload.processed = True
    csv_upload.save()


def view_data(request, upload_id):
    """View uploaded CSV data with rankings"""
    csv_upload = get_object_or_404(CSVUpload, id=upload_id)
    
    # Get top ranked records
    top_records_queryset = csv_upload.records.all()[:20]  # Top 20
    top_records = list(top_records_queryset)  # Convert to list to avoid indexing issues
    
    # Get column names from first record
    columns = []
    if top_records:
        columns = list(top_records[0].data.keys())
        # Remove calculated_score and normalized columns from display
        columns = [col for col in columns if not col.endswith('_normalized') and col != 'calculated_score']
    
    # Calculate score range for display
    highest_score = top_records[0].score if top_records else 0
    lowest_score = top_records[-1].score if len(top_records) > 1 else highest_score
    
    context = {
        'csv_upload': csv_upload,
        'top_records': top_records,
        'columns': columns,
        'total_records': csv_upload.records.count(),
        'highest_score': highest_score,
        'lowest_score': lowest_score,
    }
    
    return render(request, 'core/view_data.html', context)


def chat_with_data(request, upload_id):
    """Chat interface for querying data using Ollama"""
    csv_upload = get_object_or_404(CSVUpload, id=upload_id)
    
    # Get or create chat session
    session_id = request.session.get(f'chat_session_{upload_id}')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session[f'chat_session_{upload_id}'] = session_id
    
    chat_session, created = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={'csv_upload': csv_upload}
    )
    
    # Get chat history
    messages = chat_session.messages.all()
    
    context = {
        'csv_upload': csv_upload,
        'chat_session': chat_session,
        'messages': messages
    }
    
    return render(request, 'core/chat.html', context)


@csrf_exempt
def send_message(request, upload_id):
    """Handle chat message and get response from Ollama"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    csv_upload = get_object_or_404(CSVUpload, id=upload_id)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get chat session
        session_id = request.session.get(f'chat_session_{upload_id}')
        if not session_id:
            return JsonResponse({'error': 'No chat session found'}, status=400)
        
        chat_session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Save user message
        ChatMessage.objects.create(
            session=chat_session,
            message_type='user',
            content=user_message
        )
        
        # Get data context for the AI
        top_records = csv_upload.records.all()[:10]
        data_context = []
        for record in top_records:
            data_context.append(f"Rank {record.rank}: {record.data}")
        
        # Create context for Ollama
        context = f"""
        You are an AI assistant helping to analyze CSV data for QuickPickHR.
        Here is the top 10 ranked data from the uploaded CSV:
        
        {chr(10).join(data_context)}
        
        Total records: {csv_upload.records.count()}
        
        Please answer the user's question about this data. Be helpful and provide specific insights based on the data shown.
        """
        
        # Send to Ollama
        ollama_response = query_ollama(user_message, context)
        
        # Save assistant response
        ChatMessage.objects.create(
            session=chat_session,
            message_type='assistant',
            content=ollama_response
        )
        
        return JsonResponse({
            'response': ollama_response,
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def query_ollama(user_message, context):
    """Query local Ollama instance"""
    try:
        # Ollama API endpoint (default local installation)
        ollama_url = "http://localhost:11434/api/generate"
        
        prompt = f"""
        Context: {context}
        
        User Question: {user_message}
        
        Please provide a helpful answer based on the data context provided above.
        """
        
        payload = {
            "model": "granite3.3:2b",  # Change this to your preferred model
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(ollama_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Sorry, I could not generate a response.')
        else:
            return f"Error connecting to Ollama (Status: {response.status_code}). Please make sure Ollama is running locally."
            
    except requests.exceptions.ConnectionError:
        return "Could not connect to Ollama. Please make sure Ollama is installed and running on your system. You can start it with 'ollama serve'."
    except requests.exceptions.Timeout:
        return "Request to Ollama timed out. Please try again."
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"


def delete_upload(request, upload_id):
    """Delete uploaded CSV and all related data"""
    if request.method == 'POST':
        csv_upload = get_object_or_404(CSVUpload, id=upload_id)
        csv_upload.delete()
        messages.success(request, 'CSV data deleted successfully!')
    
    return redirect('home')
