class CompareFile:
    def __init__(self, old_file, new_file, output_file):
        self.old_file = old_file
        self.new_file = new_file
        self.output_file = output_file

    def get_urls_from_file(self, file_path):
        with open(file_path, 'r') as f:
            return set(line.strip() for line in f if line.strip())

    def write_to_file(self, urls):
        with open(self.output_file, 'w') as f:
            for url in sorted(urls):
                f.write(url + '\n')

    def get_unique_url(self):
        # Load URLs
        urls_file1 = self.get_urls_from_file(self.old_file)
        urls_file2 = self.get_urls_from_file(self.new_file)

        # Find URLs that are in file2 but NOT in file1
        unique_urls = urls_file2 - urls_file1  # set difference

        # Write to output file
        self.write_to_file(unique_urls)

        print(f"Unique URLs written to {self.output_file}")
