from googlesearch import search

class SearchEngine:
    @staticmethod
    def search(query):
        print(f"   [Engine] Searching Google silently for: '{query}'...")
        try:
            # advanced=True gets the Title and Description, not just the URL
            search_results = search(query, num_results=3, advanced=True)
            
            results_text = "--- SEARCH RESULTS ---\n"
            count = 0
            
            for result in search_results:
                count += 1
                results_text += f"Result {count}:\n"
                results_text += f"Title: {result.title}\n"
                results_text += f"Summary: {result.description}\n\n"
            
            if count == 0:
                return "No results found. The search returned nothing."
                
            return results_text
            
        except Exception as e:
            return f"Search Engine Error: {e}"

# Test it directly
if __name__ == "__main__":
    print(SearchEngine.search("Who is the president of America right now"))