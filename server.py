import socket
import threading
import json

# Supported bases
SUPPORTED_BASES = {
    'binary': 2,
    'octal': 8,
    'decimal': 10,
    'hexadecimal': 16
}

# Function to perform number conversions between any two bases
def convert_number(source_base, target_base, number):
    try:
        # Validate bases
        if source_base not in SUPPORTED_BASES:
            return {"error": f"Unsupported source base: {source_base}. Supported bases are: {list(SUPPORTED_BASES.keys())}"}
        if target_base not in SUPPORTED_BASES:
            return {"error": f"Unsupported target base: {target_base}. Supported bases are: {list(SUPPORTED_BASES.keys())}"}
        
        # Convert number from source base to decimal
        decimal_number = int(number, SUPPORTED_BASES[source_base])
        
        # Convert decimal number to target base
        if target_base == 'binary':
            converted = bin(decimal_number)
        elif target_base == 'octal':
            converted = oct(decimal_number)
        elif target_base == 'decimal':
            converted = str(decimal_number)
        elif target_base == 'hexadecimal':
            converted = hex(decimal_number)
        else:
            # This should not happen due to earlier validation
            return {"error": f"Conversion to {target_base} not implemented."}
        
        return {"result": converted}
    
    except ValueError:
        return {"error": f"Invalid number '{number}' for base {source_base}."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# Function to handle client connections
def handle_client(client_socket, addr):
    print(f"Connected to {addr}")
    try:
        while True:
            # Receive data from client
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                break
            print(f"Received data from {addr}: {data}")
            
            try:
                # Parse JSON request
                request = json.loads(data)
                source_base = request.get('source_base', '').lower()
                target_base = request.get('target_base', '').lower()
                number = request.get('number', '')
                
                # Perform conversion
                response = convert_number(source_base, target_base, number)
                
            except json.JSONDecodeError:
                response = {"error": "Invalid JSON format."}
            except Exception as e:
                response = {"error": f"An error occurred: {str(e)}"}
            
            # Send JSON response
            response_json = json.dumps(response)
            client_socket.sendall(response_json.encode('utf-8'))
            print(f"Sent response to {addr}: {response_json}")
    except ConnectionResetError:
        print(f"Connection with {addr} was closed unexpectedly.")
    finally:
        client_socket.close()
        print(f"Disconnected from {addr}")

def start_server(host='localhost', port=9089):
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))  # Bind to host on specified port
    server_socket.listen(5)  # Listen for incoming connections
    print(f"Server is listening on {host}:{port}...")
    
    try:
        while True:
            # Accept client connection
            client_socket, addr = server_socket.accept()
            # Handle client in a new thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
