# main.py
import os
import json
from datetime import datetime

class Solution:
    def __init__(self):
        self.created_at = datetime.now()
    
    def process(self, data):
        """Main processing function"""
        print(f"Processing data: {data}")
        return {"status": "success", "timestamp": self.created_at.isoformat()}
    
    def validate_input(self, data):
        """Validate input data"""
        if not data:
            raise ValueError("Data cannot be empty")
        return True

if __name__ == "__main__":
    solution = Solution()
    result = solution.process("sample data")
    print(json.dumps(result, indent=2))