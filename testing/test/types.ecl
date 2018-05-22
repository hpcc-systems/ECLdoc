EXPORT types := MODULE
	EXPORT v1 := RECORD
		REAL8 u;
		REAL8 v;
	END;

	EXPORT DATASET(v1) mod_1 := FUNCTION
        v1 tr({REAL8 x} y) := TRANSFORM
            SELF.u := y.x;
            SELF.v := y.x * 2.0;
        END;
        RETURN PROJECT(DATASET([{1}, {2}], {REAL8 x}), tr(LEFT));
    END;

    EXPORT mod_1_1(TYPEOF(mod_1) x) := x;

	EXPORT DATASET({STRING20 a}) mod_2 := DATASET([], {STRING20 a});

	EXPORT mod_3 := ENUM(UNSIGNED8, a, b, c, d);

	EXPORT mod_4 := mod_3;

	EXPORT mod_41 := MODULE
		EXPORT v41 := 3.4;
	END;

    /**
    * mod_5
    * @param x abcd
    * @return module
    */
	EXPORT mod_5(REAL8 x) := MODULE
		EXPORT v6 := x * 4;
	END;

	EXPORT mod_6(REAL8 x) := mod_5(x);

	EXPORT mod_7(mod_5 y, REAL8 z) := FUNCTION
		RETURN y(0.5).v6 + z;
	END;

	EXPORT mod_8(mod_3 a1) := a1 * 9;

	EXPORT mod_9(mod_7 x) := x(mod_5, 3.0);

    EXPORT mod_90(REAL8 z) := FUNCTION
        RETURN z * 2;
    END;

	/*EXPORT ScaleInt := TYPE
        EXPORT REAL LOAD(INTEGER4 I ) := I / 100;
        EXPORT INTEGER4 STORE(REAL R) := ROUND(R * 100);
    END;*/

    EXPORT mod_10 := RECORD
    	REAL8 u; //ScaleInt y;
    END;

    EXPORT mod_11(DATASET(mod_10) y) := y;

    EXPORT D1 := DATASET([{1, 2, 3}], {UNSIGNED4 F1, REAL8 f2, REAL8 f3});

    EXPORT mod_12 := RECORD
    	D1.F1;
    	gcount := COUNT(GROUP);
    END;

    EXPORT mod_13 := TABLE(D1, mod_12, F1);

    EXPORT v2 := RECORD
    	UNSIGNED4 w1;
    	UNSIGNED4 w2;
    	UNSIGNED4 w3;
    END;

    EXPORT v2 v1tov2(v1 x) := TRANSFORM
    	SELF.w1 := x.v;
    	SELF.w2 := x.u;
    	SELF.w3 := x.u * x.v;
    END;

    EXPORT TYPEOF(mod_1) mod_14 := DATASET([{1, 3}], v1);

    v3 := RECORD
    	REAL8 w1;
    END;
    EXPORT DATASET(v3) mod_15 := DATASET([{1}], v3);

    EXPORT v4 := RECORD(v2)
    	REAL8 w4;
    END;

    EXPORT v5 := RECORD
    	v1 OR v2;
    	REAL8 w4;
    	DATASET(v2) w5;
    END;

    EXPORT v5_1(DATASET({v5, real8 y}) x) := x;

    EXPORT { REAL8 a } mod_17(v1 x) := TRANSFORM
    	SELF.a := x.v;
    END;

    EXPORT mod_18(REAL8 x(REAL8 z), REAL8 y) := FUNCTION
    	RETURN x(y);
    END;

    EXPORT mod_19(REAL8 w) := w * 9;

    EXPORT mod_20(mod_19 x) := mod_18(x, 3.0);

    EXPORT mod_21 := mod_20(mod_19);

    EXPORT mod_22(REAL8 w) := w * 4.0;

    EXPORT mod_23 := mod_20(mod_22);

    EXPORT mod_24(REAL8 y(REAL8 z(REAL8 u)), REAL8 x(REAL8 y)) := y(x);

    EXPORT REAL8 mod_25(REAL8 x(REAL8 y)) := x(4.0);

    EXPORT mod_26 := mod_24(mod_25, mod_22);

    EXPORT mod_1 mod_27 := mod_1;

END;
