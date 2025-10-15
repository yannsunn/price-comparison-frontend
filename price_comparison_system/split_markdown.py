
import json
import os

def split_markdown_into_chunks(input_file, output_dir, chunk_size=50):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        markdown_content = data.get('markdown', '')

        if not markdown_content:
            print("Markdown content not found in the JSON file.")
            return

        lines = markdown_content.split('\n')
        chunk_num = 1
        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i + chunk_size])
            output_file_path = os.path.join(output_dir, f'chunk_{chunk_num}.md')
            with open(output_file_path, 'w', encoding='utf-8') as chunk_file:
                chunk_file.write(chunk)
            print(f"Created chunk: {output_file_path}")
            chunk_num += 1

    except FileNotFoundError:
        print(f"Error: File not found at {input_file}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    input_file = '/home/ubuntu/.mcp/tool-results/2025-10-14_14-05-39_firecrawl_firecrawl_scrape.json'
    output_dir = 'price_comparison_system/markdown_chunks'
    split_markdown_into_chunks(input_file, output_dir)

