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

        RunOptions(Srting requestId,int maxConcurrency){
            this.requestId = requestId.strip();
            this.maxConcurrency = maxConcurrency;
        }
    }
    public static void main(String[] args) {
        RunOptions options = new RunOptions(" batch-001 ",2);

        System.out.println(options.requestId);
        System.out.println(options.maxConcurrency);
    }
}