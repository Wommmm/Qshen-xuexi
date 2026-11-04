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
    static void runWorker(Worker worker){
        try{
            String result = worker.execute();
            System.out.println("结果"+result);
        } catch (RuntimeException e){
            System.out.println("捕获到异常："+e.getMessage());
        }
    }

    public static void main(String[] args) {
        runWorker(new SuccessWork());
        runWorker(new ErrorWork());
        System.out.println("结束");
    }
}