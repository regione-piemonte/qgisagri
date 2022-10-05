set define off;

ALTER TABLE QGIS_T_SUOLO_LAVORAZIONE ADD 
    ( 
     DATA_LAVORAZIONE DATE 
    ) 
;


alter type OBJ_SUOLI_IN_LAVORAZIONE add attribute ID_TIPO_MOTIVO_SOSPENSIONE number cascade;
alter type OBJ_SUOLI_IN_LAVORAZIONE add attribute FLAG_SOSPENSIONE varchar2(1) cascade;
alter type OBJ_SUOLI_IN_LAVORAZIONE add attribute DESCRIZIONE_SOSPENSIONE varchar2(200) cascade;

CREATE TABLE QGIS_T_LAVORAZ_BYPASS 
    ( 
     ID_LAVORAZ_BYPASS           NUMBER (10)  NOT NULL , 
     ID_EVENTO_LAVORAZIONE       NUMBER (10)  NOT NULL , 
     FLAG_DIFF_AREA_SUOLI        VARCHAR2 (1)  NOT NULL , 
     FLAG_CESSATI_SUOLI          VARCHAR2 (1)  NOT NULL , 
     ANOMALIA                    VARCHAR2 (4000) , 
     DATA_AGGIORNAMENTO          DATE  NOT NULL , 
     EXT_ID_UTENTE_AGGIORNAMENTO NUMBER (10)  NOT NULL 
    ) 
TABLESPACE SITIPIOPR_TBL;

ALTER TABLE QGIS_T_LAVORAZ_BYPASS 
    ADD CONSTRAINT CK_FLAG_09 
    CHECK (FLAG_DIFF_AREA_SUOLI IN ('N', 'S')) 
;

ALTER TABLE QGIS_T_LAVORAZ_BYPASS 
    ADD CONSTRAINT CK_FLAG_10 
    CHECK (FLAG_CESSATI_SUOLI IN ('N', 'S')) 
;

ALTER TABLE QGIS_T_LAVORAZ_BYPASS 
    ADD CONSTRAINT PK_QGIS_T_LAVORAZ_BYPASS PRIMARY KEY ( ID_LAVORAZ_BYPASS ) USING INDEX TABLESPACE SITIPIOPR_IDX;

ALTER TABLE QGIS_T_LAVORAZ_BYPASS 
    ADD CONSTRAINT FK_QGIS_T_EVENTO_LAVORAZION_05 FOREIGN KEY 
    ( 
     ID_EVENTO_LAVORAZIONE
    ) 
    REFERENCES QGIS_T_EVENTO_LAVORAZIONE 
    ( 
     ID_EVENTO_LAVORAZIONE
    ) 
;

CREATE SEQUENCE SEQ_QGIS_T_LAVORAZ_BYPASS 
START WITH 1 
    NOCACHE ;

ALTER TABLE QGIS_T_LAVORAZ_BYPASS ADD 
    ( 
     FLAG_AREA_MIN_SUOLI VARCHAR2 (1)  NOT NULL 
    ) 
;


ALTER TABLE QGIS_T_LAVORAZ_BYPASS 
    ADD 
        CONSTRAINT CK_FLAG_11 CHECK (FLAG_AREA_MIN_SUOLI IN ('N', 'S')) 
;

grant select on QGIS_T_SUOLO_RILEVATO to smrgaa;
grant select on QGIS_T_SUOLO_LAVORAZIONE to smrgaa;
grant select on QGIS_T_SUOLO_PROPOSTO to smrgaa;

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


	

