/**
* Basic Example with :
* records, interface, function,
* modules, transform, embed,
* macros and functionmacro
*/

EXPORT example := MODULE
  EXPORT rec_1 := RECORD
    REAL8 f;
    REAL8 g;
  END;

  EXPORT rec_2 := RECORD
    UNSIGNED4 a;
    REAL8 b;
    REAL8 g;
  END;

  EXPORT interface_ex := INTERFACE
  	SHARED UNSIGNED4  iface_v1;
  	EXPORT STRING25  iface_v3 := '';
  END;

  EXPORT func_1(REAL8 x, STRING25 y) := FUNCTION
    RETURN 2 * x;
  END;

  SHARED rec_2 trans_1(rec_1 rec) := TRANSFORM, SKIP(rec.f > 2)
    SELF.a := rec.f;
    SELF.b := rec.f + rec.g;
    SELF.g := rec.g;
  END;

  EXPORT DATASET(rec_2) func_2(DATASET(rec_1) d) := FUNCTION
  	RETURN PROJECT(d, trans_1(LEFT));
  END;

  EXPORT mod_1(REAL8 a) := MODULE
  	EXPORT pi_w := 2.3;
  END;

  EXPORT mod_2 := MODULE
    EXPORT pi_wo := 2.3;
  END;


  EXPORT DATA cpp_1(REAL8 varcpp) := BEGINC++

  ENDC++;

  EXPORT funcmacro_1(num) := FUNCTIONMACRO
    LOCAL numPlus := num + 1;
    RETURN numPlus;
  ENDMACRO;

  EXPORT macro_1(num_1, num_2) := MACRO
    EXPORT attrname := num_1 + num_2;
  ENDMACRO;

  EXPORT macro_2 := MACRO
  	EXPORT attr := 2.0;
  ENDMACRO;
END;