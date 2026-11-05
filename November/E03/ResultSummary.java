package November.E03;

import java.util.List;// 列表接口
import java.util.Map;//键值映射接口
import java.util.HashMap;//Map的一种具体实现

public class ResultSummary {
    public static void main(String[] args) {
        List<String> statuses = List.of(
        "success","error","timeout"
        );
        Map<String,Integer> counts = new HashMap<>(); 
        counts.put("success",0);
        counts.put("error",0);
        counts.put("timeout",0);
        
        for(String status : statuses){
            int current = counts.getOrDefault(status,0);
                 counts.put(status,current + 1);
        }
        System.out.println(counts);

    }
}
