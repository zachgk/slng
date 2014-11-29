/**
 * Created by Zach Kimberg on 11/29/14.
 */

import net.sf.json.JSONObject;

import java.io.FileInputStream;
import java.io.InputStream;
import java.io.PrintWriter;
public class Convert {
    public static void main(String[] args) throws Exception{
        InputStream is = new FileInputStream("input.slng");
        Converter c = new Converter();
        JSONObject prog = c.convert(is);
        PrintWriter writer = new PrintWriter("output.json");
        writer.println(prog.toString());
        writer.close();
    }
}
