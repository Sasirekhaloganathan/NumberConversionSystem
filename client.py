import socket
import streamlit as st
import json

# Supported bases for user selection
SUPPORTED_BASES = ['binary', 'octal', 'decimal', 'hexadecimal']

def convert_number(source_base, target_base, number):
    """
    Connect to the server, send the conversion request, and receive the result.
    """
    request = {
        "source_base": source_base,
        "target_base": target_base,
        "number": number
    }
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(5)  # 5 seconds timeout
            st.info("Connecting to the server...")
            client_socket.connect(('localhost', 9089))
            st.success("Connected to the server.")
            
            # Send JSON request
            request_json = json.dumps(request)
            client_socket.sendall(request_json.encode('utf-8'))
            st.info(f"Sent request: {request_json}")
            
            # Receive JSON response
            response_data = client_socket.recv(4096).decode('utf-8')
            st.info(f"Received response: {response_data}")
            
            # Parse JSON response
            response = json.loads(response_data)
            
            return response
    except socket.timeout:
        st.error("Connection timed out. The server may be busy or not responding.")
    except ConnectionRefusedError:
        st.error("Failed to connect to the server. Make sure the server is running.")
    except json.JSONDecodeError:
        st.error("Received invalid JSON response from the server.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
    return None

def main():
    # Set the page configuration
    st.set_page_config(
        page_title="Number Conversion System",
        page_icon="🔢",
        layout="centered",
        initial_sidebar_state="auto"
    )
    
    st.title("Number Conversion System")
    st.write("Convert numbers between different bases easily.")
    
    # Sidebar for base selection
    st.sidebar.header("Conversion Settings")
    
    source_base = st.sidebar.selectbox("Select Source Base", SUPPORTED_BASES, index=2)  # Default: decimal
    target_base = st.sidebar.selectbox("Select Target Base", SUPPORTED_BASES, index=0)  # Default: binary
    
    # Input Field
    number = st.text_input("Enter Number to Convert:")
    
    # Convert Button
    if st.button("Convert"):
        if not number.strip():
            st.warning("Please enter a number to convert.")
        elif source_base == target_base:
            st.warning("Source and target bases are the same. Please select different bases.")
        else:
            # Perform conversion
            response = convert_number(source_base, target_base, number)
            if response:
                if 'result' in response:
                    st.subheader("Conversion Result:")
                    st.success(response['result'])
                elif 'error' in response:
                    st.error(response['error'])
                else:
                    st.error("Unexpected response from the server.")

if __name__ == "__main__":
    main()
