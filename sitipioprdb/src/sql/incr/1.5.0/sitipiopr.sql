set define off;

CREATE TABLE QGIS_D_ESITO 
    ( 
     ID_ESITO    NUMBER (4)  NOT NULL , 
     CODICE      VARCHAR2 (20)  NOT NULL , 
     DESCRIZIONE VARCHAR2 (200)  NOT NULL 
    ) 
TABLESPACE SITIPIOPR_TBL;


ALTER TABLE QGIS_D_ESITO 
    ADD CONSTRAINT PK_QGIS_D_ESITO PRIMARY KEY ( ID_ESITO  ) USING INDEX TABLESPACE SITIPIOPR_IDX;
	
INSERT INTO QGIS_D_ESITO(ID_ESITO,DESCRIZIONE,CODICE) VALUES(1,'Salvataggio in corso','SC');
INSERT INTO QGIS_D_ESITO(ID_ESITO,DESCRIZIONE,CODICE) VALUES(2,'Salvataggio istanza in corso','SIC');
INSERT INTO QGIS_D_ESITO(ID_ESITO,DESCRIZIONE,CODICE) VALUES(3,'Salvataggio terminato','ST');
INSERT INTO QGIS_D_ESITO(ID_ESITO,DESCRIZIONE,CODICE) VALUES(4,'Salvataggio istanza terminato con errori','SITE');

COMMIT;

ALTER TABLE QGIS_T_EVENTO_LAVORAZIONE ADD 
    ( 
     ID_ESITO NUMBER (4) 
    ) 
;

ALTER TABLE QGIS_T_EVENTO_LAVORAZIONE 
    ADD CONSTRAINT FK_QGIS_D_ESITO_01 FOREIGN KEY 
    ( 
     ID_ESITO
    ) 
    REFERENCES QGIS_D_ESITO 
    ( 
     ID_ESITO
    );
	
CREATE TABLE QGIS_D_PARAMETRO 
    ( 
     CODICE VARCHAR2 (20)  NOT NULL , 
     VALORE VARCHAR2 (4000)  NOT NULL , 
     NOTE   VARCHAR2 (4000) 
    ) 
TABLESPACE SITIPIOPR_TBL;


ALTER TABLE QGIS_D_PARAMETRO 
    ADD CONSTRAINT PK_QGIS_D_PARAMETRO PRIMARY KEY ( CODICE  ) USING INDEX TABLESPACE SITIPIOPR_IDX;
	
ALTER TABLE QGIS_T_VERSIONE_PARTICELLA ADD 
    ( 
     FLAG_INFO_3D VARCHAR2 (1) DEFAULT 'N'  NOT NULL 
    ) 
;


ALTER TABLE QGIS_T_VERSIONE_PARTICELLA 
    ADD 
        CONSTRAINT CK_FLAG_12 CHECK (FLAG_INFO_3D IN ('N', 'S')) 
;

-- Script grants
declare
  
  Procedure CreateGrantToUser is
  TYPE tpUser IS RECORD (nomeUser  VARCHAR2(30),
  	   		   		     Comando   VARCHAR2(300));
						   
  TYPE typTbUser IS TABLE OF tpUser INDEX BY BINARY_INTEGER;						   
  
  tUser    typTbUser;
  
  begin
    tUser(1).nomeUser := 'SITIPIOPR_RW';
    tUser(1).comando  := 'grant select,insert, update, delete on ';
	
	FOR i IN tUser.FIRST..tUser.LAST LOOP
	--grant sulle tabelle
    for c in ( 
       select tUser(i).comando||tb.table_name||' to '||tUser(i).nomeUser cmd from user_tables tb where tb.table_name != 'DBG_GATE_CALLS'
    ) loop
      execute immediate c.cmd;
    end loop;

    -- Grant sulle sequence
    for c in ( 
       select 'grant select,alter on '||se.sequence_name||' to '||tUser(i).nomeUser cmd from user_sequences se
    ) loop 
      execute immediate c.cmd;
    end loop;

    -- Grant su Procedure/Funzioni/Package
    for c in ( 
       select distinct 'grant execute on '||pr.object_name||' to '||tUser(i).nomeUser cmd from user_procedures pr 
    ) loop
      execute immediate c.cmd;
    end loop;
	
	-- Grant su types
    for c in ( 
       select distinct 'grant execute on '||pr.type_name||' to '||tUser(i).nomeUser cmd from user_types pr where instr(pr.type_name,'SYS') = 0 
    ) loop
      execute immediate c.cmd;
    end loop;
	
	-- Grant su viste
    for c in ( 
       select distinct 'grant select on '||vi.view_name||' to '||tUser(i).nomeUser cmd from user_views vi 
    ) loop
      execute immediate c.cmd;
    end loop;
    
    end loop;
  end;                           
begin
  CreateGrantToUser;
end;
/


	

