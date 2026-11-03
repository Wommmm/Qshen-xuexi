public class WorkerDemo {
    interface Worker{
        String execute();
    }
    static class SuccessWork implements Worker{
        @Override
        public String execute() {
            return "Success";
        }
    }
    static class ErrorWork implements Worker{
        @Override
        public String execute(){
            throw new RuntimeException("Error");
        } 
    }

    public static void main(String[] args) {
    Worker worker = new SuccessWork();
    System.out.println(worker.execute());

    Worker failedWorker = new ErrorWork();

    try {
        String result = failedWorker.execute();
        System.out.println(result);
    } catch (RuntimeException e) {
        System.out.println("捕获到异常：" + e.getMessage());
    }

    System.out.println("程序继续执行");
    } // 结束 main
}     // 结束 WorkerDemo 类