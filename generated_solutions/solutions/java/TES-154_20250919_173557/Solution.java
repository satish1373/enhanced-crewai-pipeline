// Solution.java
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

public class Solution {
    private LocalDateTime createdAt;
    
    public Solution() {
        this.createdAt = LocalDateTime.now();
    }
    
    public Map<String, Object> process(String data) {
        System.out.println("Processing data: " + data);
        
        Map<String, Object> result = new HashMap<>();
        result.put("status", "success");
        result.put("data", data);
        result.put("timestamp", createdAt.toString());
        
        return result;
    }
    
    public boolean validateInput(String data) {
        if (data == null || data.isEmpty()) {
            throw new IllegalArgumentException("Data cannot be empty");
        }
        return true;
    }
    
    public static void main(String[] args) {
        Solution solution = new Solution();
        Map<String, Object> result = solution.process("sample data");
        System.out.println(result);
    }
}