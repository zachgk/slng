/**
 * Created by Zach Kimberg on 11/29/14.
 */

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
import org.antlr.v4.runtime.*;

import java.io.InputStream;
import java.util.List;

public class Converter {
    public JSONObject convert(InputStream is) throws Exception{
        ANTLRInputStream in = new ANTLRInputStream(is);
        superLangLexer l = new superLangLexer(in);
        superLangParser p = new superLangParser(new CommonTokenStream(l));

        final JSONObject prog = new JSONObject();
        final JSONObject types = new JSONObject();
        final JSONObject vars = new JSONObject();
        final JSONArray output = new JSONArray();

        p.addParseListener(new superLangBaseListener() {

            @Override
            public void exitProgram(superLangParser.ProgramContext ctx) {
                List<superLangParser.StatementContext> statements = ctx.statement();
                for (superLangParser.StatementContext statement : statements) {
                }
            }

            @Override
            public void exitTypeDeclaration(superLangParser.TypeDeclarationContext ctx) {
                JSONObject type = new JSONObject();
                String name = ctx.UpperName().getText();
                type.put("type", name);
                List<superLangParser.BindingDeclarationContext> bindings = ctx.bindingDeclaration();
                if(bindings.size() > 0) {
                    JSONArray properties = new JSONArray();
                    for(superLangParser.BindingDeclarationContext bctx : bindings) {
                        JSONObject property = new JSONObject();
                        property.put("binding",bctx.LowerName().getText());
                        if(bctx.expression() != null) property.put("expression",bctx.expression().getText());
                        if(bctx.dataType() != null) property.put("type",bctx.dataType().getText());
                        properties.add(property);
                    }
                    type.put("properties",properties);
                }
                types.put(name,type);
            }

            @Override
            public void exitVarDeclaration(superLangParser.VarDeclarationContext ctx) {
                JSONObject var = new JSONObject();
                String name = ctx.LowerName().getText();
                var.put("name",name);
                var.put("type",ctx.construction().UpperName().getText());
                JSONObject expressions = new JSONObject();
                for (superLangParser.AssignmentDeclarationContext param : ctx.construction().params().assignmentDeclaration()) {
                    expressions.put(param.LowerName().getText(),param.expression().getText());
                }
                var.put("expressions",expressions);
                vars.put(name,var);
            }

            @Override
            public void exitOutput(superLangParser.OutputContext ctx) {
                output.add(ctx.expression().getText());
            }
        });
        p.program();
        if(types.size() > 0) prog.put("types", types);
        if(vars.size() > 0) prog.put("vars", vars);
        if(output.size() > 0) prog.put("output",output);
        return prog;
    }
}
