/**
 * Created by Zach Kimberg on 11/29/14.
 */
import net.sf.json.JSONObject;

import java.io.FileInputStream;
import java.io.InputStream;

public class Run {
    public static void main(String[] args) throws Exception{
        InputStream is = new FileInputStream("src/main/resources/example.slng");
        Converter c = new Converter();
        JSONObject prog = c.convert(is);
        System.out.println(prog);
    }
}
