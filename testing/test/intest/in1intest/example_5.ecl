/**
* Basic ECL file : without enclosing module
* Demos records, interfcae, functions, modules, embed, transform, macros
*/

rec_1 := RECORD
  REAL8 f;
  REAL8 g;
END;

rec_2 := RECORD
  UNSIGNED4 a;
  REAL8 b;
  REAL8 g;
END;

interface_ex := INTERFACE
	SHARED UNSIGNED4  iface_v1;
	EXPORT STRING25  iface_v3 := '';
END;

func_1(REAL8 x, STRING25 y) := FUNCTION
  RETURN 2 * x;
END;

rec_2 trans_1(rec_1 rec) := TRANSFORM, SKIP(rec.f > 2)
  SELF.a := rec.f;
  SELF.b := rec.f + rec.g;
  SELF.g := rec.g;
END;

DATASET(rec_2) func_2(DATASET(rec_1) d) := FUNCTION
	RETURN PROJECT(d, trans_1(LEFT));
END;

mod_1(REAL8 a) := MODULE
	EXPORT pi_w := 2.3;
END;

mod_2 := MODULE
  EXPORT pi_wo := 2.3;
END;


DATA cpp_1(REAL8 varcpp) := BEGINC++

ENDC++;

funcmacro_1(num) := FUNCTIONMACRO
  LOCAL numPlus := num + 1;
  RETURN numPlus;
ENDMACRO;

macro_1(num_1, num_2) := MACRO
  EXPORT attrname := num_1 + num_2;
ENDMACRO;

macro_2 := MACRO
	EXPORT attr := 2.0;
ENDMACRO;

a := func_1(2, 'TEST');
OUTPUT(a);

b := func_2(DATASET([{2,3}, {3,4}], rec_1));
OUTPUT(b);

