// SolutionTest.java
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;

public class SolutionTest {
    private Solution solution;
    
    @BeforeEach
    void setUp() {
        solution = new Solution();
    }
    
    @Test
    void testProcess() {
        Map<String, Object> result = solution.process("test data");
        assertEquals("success", result.get("status"));
        assertEquals("test data", result.get("data"));
        assertNotNull(result.get("timestamp"));
    }
    
    @Test
    void testValidateInputValid() {
        assertTrue(solution.validateInput("valid data"));
    }
    
    @Test
    void testValidateInputEmpty() {
        assertThrows(IllegalArgumentException.class, () -> {
            solution.validateInput("");
        });
    }
}