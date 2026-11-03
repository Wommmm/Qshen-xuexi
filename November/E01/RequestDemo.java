// public class RequestDemo {
//     public static void main(String[] args) {
//         String requestId = " batch-001 ";
//         int maxConcurrency = 2;

//          if (requestId == null || requestId.isBlank()) {
//             throw new IllegalArgumentException("requestId 不能为空");
//         }

//         requestId = requestId.strip();

//         requestId = requestId.strip();
//         if (maxConcurrency <1 || maxConcurrency > 4){
//             throw new IllegalArgumentException("maxConcurrency must be between 1 and 4");
//         }
//         System.out.println(requestId);
//         System.out.println(maxConcurrency);
//     }
// }

public class RequestDemo{
    static class RunOptions{
        String requestId;
        int maxConcurrency;

        RunOptions(String requestId,int maxConcurrency){
            if(requestId == null || requestId.isBlank()){
                throw new IllegalArgumentException("requestId 不能为空");
            }
            if (maxConcurrency <1 || maxConcurrency >4){
                throw new IllegalArgumentException("并发数必须在1~4");
            }

            this.requestId = requestId.strip();
            this.maxConcurrency = maxConcurrency;
            
        }
    }
    public static void main(String[] args){
        RunOptions options = new RunOptions(" batch-001 ",2);
        System.out.println("合法 id"+options.requestId);
        System.out.println("合法并发数"+options.maxConcurrency);

        try {
            new RunOptions(" ",2);
            System.out.println("错误：空白 ID 已经放行");
        }
        catch(IllegalArgumentException e){
            System.out.println("错误："+e.getMessage());
        
        }

        System.out.println("结束");
      }

    }
 