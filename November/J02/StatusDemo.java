package November.J02;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;

public class StatusDemo {
    // 示例：接收一个状态字符串，返回它是否代表成功。
    static boolean isSuccess(String status) {
        return "success".equals(status);
    }

    // 练习：success、error、timeout 返回 true，其余返回 false。
    static boolean isValidStatus(String status) {
        return "success".equals(status) || "error".equals(status) || "timeout".equals(status);
        
    }

    static String describeStatus(String status)
    {
        if (!isValidStatus(status)){
            throw new IllegalArgumentException("无效的状态"+status);
        }
        if ("success".equals(status)){
            return "成功";
        } else if ("error".equals(status)){
            return "失败";
        } else {
            return "超时";
        }

    }
    static int countFailures(String[] statuses){
        return selectFailures(statuses).size();
    }

    static List<String> selectFailures(String[] statuses){
        List<String> selected = new ArrayList<>();
        for (String status : statuses){
            if (!isValidStatus(status)){
                throw new IllegalArgumentException("无效的状态"+status);
            }
            if ("error".equals(status)||"timeout".equals(status))
                selected.add(status);
        }
        return selected;
    }
    static Map<String, Integer> countByStatus(String[] statuses){
        Map<String, Integer> counts = new HashMap<>();
        counts.put("success",0 );
        counts.put("error",0);
        counts.put("timeout",0);
        for (String status : statuses){
            if (!isValidStatus(status)){
                throw new IllegalArgumentException("无效的状态"+status);
            }
                counts.put(status, counts.get(status)+1);
        }
        return counts;
    }

    public static void main(String[] args) {
            String[] statuses = {
        "success", "error", "timeout", "success", "error"
    };
        System.out.println("未成功数量：" + countFailures(statuses));
        System.out.println("未成功状态：" + selectFailures(statuses));
        System.out.println("成功判断：" + isSuccess("success"));
        System.out.println("success 合法：" + isValidStatus("success"));
        System.out.println("error 合法：" + isValidStatus("error"));
        System.out.println("timeout 合法：" + isValidStatus("timeout"));
        System.out.println("unknown 合法：" + isValidStatus("unknown"));
        System.out.println(describeStatus("success"));
    }
}
