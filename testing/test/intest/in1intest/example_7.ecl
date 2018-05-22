/**
* Basic Type Example
* Source Code copied from ECL Documentation
*/

EXPORT example_7 := MODULE
    SHARED STRING4 Rev(STRING4 S) := S[4] + S[3] + S[2] + S[1];
    SHARED ReverseString4 := TYPE
        EXPORT STRING4 LOAD(STRING4 S) := Rev(S);
        EXPORT STRING4 STORE(STRING4 S) := Rev(S);
    END;
    SHARED NeedC(INTEGER len) := TYPE
        EXPORT STRING LOAD(STRING S) := 'C' + S[1..len];
        EXPORT STRING STORE(STRING S) := S[2..len+1];
        EXPORT INTEGER PHYSICALLENGTH(STRING S) := len;
    END;
    SHARED ScaleInt := TYPE
        EXPORT REAL LOAD(INTEGER4 I ) := I / 100;
        EXPORT INTEGER4 STORE(REAL R) := ROUND(R * 100);
    END;
    EXPORT R := RECORD
        ReverseString4 F1;
        NeedC(5) F2;
        ScaleInt F3;
    END;
END;
