from vectore_store import initialize_vectors_function
file_path = "songs.txt"  

with open(file_path, "rb") as f:
    file_bytes = f.read()

response = initialize_vectors_function(
    file_data=file_bytes,
    filename=file_path,
)

print(response)
