set define off;

CREATE INDEX IE1_QGIS_T_REGISTRO_SUOLI ON QGIS_T_REGISTRO_SUOLI 
    ( 
     ID_SUOLO_RILEVATO ASC 
    ) 
TABLESPACE SITIPIOPR_IDX;

CREATE INDEX IE1_QGIS_T_REGISTRO_PARTICELLE ON QGIS_T_REGISTRO_PARTICELLE 
    ( 
     ID_VERSIONE_PARTICELLA ASC 
    ) 
TABLESPACE SITIPIOPR_IDX;

CREATE TABLE QGIS_T_REGISTRO_CO 
    ( 
     ID_REGISTRO_CO       NUMBER (10)  NOT NULL , 
     EXT_COD_NAZIONALE    VARCHAR2 (4)  NOT NULL , 
     FOGLIO               NUMBER (4)  NOT NULL , 
     CAMPAGNA             NUMBER (4)  NOT NULL , 
     ID_SUOLO_RILEVATO    NUMBER (10)  NOT NULL , 
     DATA_INIZIO_VALIDITA DATE  NOT NULL , 
     DATA_FINE_VALIDITA   DATE 
    ) 
TABLESPACE SITIPIOPR_TBL;


ALTER TABLE QGIS_T_REGISTRO_CO 
    ADD CONSTRAINT PK_QGIS_T_REGISTRO_CO PRIMARY KEY ( ID_REGISTRO_CO  ) USING INDEX TABLESPACE SITIPIOPR_IDX;

CREATE SEQUENCE SEQ_QGIS_T_REGISTRO_CO 
START WITH 1 
    NOCACHE ;


ALTER TABLE QGIS_T_REGISTRO_CO 
    ADD CONSTRAINT FK_QGIS_T_SUOLO_RILEVATO_07 FOREIGN KEY 
    ( 
     ID_SUOLO_RILEVATO
    ) 
    REFERENCES QGIS_T_SUOLO_RILEVATO 
    ( 
     ID_SUOLO_RILEVATO
    );
	
CREATE INDEX IE1_QGIS_T_REGISTRO_CO ON QGIS_T_REGISTRO_CO 
    ( 
     ID_SUOLO_RILEVATO ASC 
    ) 
TABLESPACE SITIPIOPR_IDX;
	
CREATE TABLE DB_LISTE_CO
(
  ID_LISTE_CO           NUMBER(5),
  PROV_RIF              VARCHAR2(20 BYTE)       NOT NULL,
  CAMPAGNA              NUMBER(4)               NOT NULL,
  DATA_INIZIO_VALIDITA  DATE                    NOT NULL,
  DATA_FINE_VALIDITA    DATE
)
TABLESPACE SITIPIOPR_TBL;

alter type obj_Suoli_In_Lavorazione add attribute Id_Tipo_Sorgente_Suolo number(4) cascade;

ALTER TABLE QGIS_D_TIPO_SORGENTE_SUOLO ADD 
    ( 
     FLAG_SOPRALLUOGO VARCHAR2 (1)  NULL 
    ) 
;


ALTER TABLE QGIS_D_TIPO_SORGENTE_SUOLO 
    ADD 
        CONSTRAINT CK_FLAG_15 CHECK (FLAG_SOPRALLUOGO IN ('N', 'S')) 
;

UPDATE QGIS_D_TIPO_SORGENTE_SUOLO
SET FLAG_SOPRALLUOGO = 'N';

COMMIT;

ALTER TABLE QGIS_D_TIPO_SORGENTE_SUOLO MODIFY FLAG_SOPRALLUOGO NOT NULL;


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


	

