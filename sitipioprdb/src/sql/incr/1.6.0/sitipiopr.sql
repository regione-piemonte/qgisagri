set define off;

CREATE TABLE QGIS_T_CXF_PARTICELLA 
    ( 
     ID_CXF_PARTICELLA    NUMBER (10)  NOT NULL , 
     EXT_COD_NAZIONALE    VARCHAR2 (4 BYTE)  NOT NULL , 
     FOGLIO               NUMBER (4)  NOT NULL , 
     PARTICELLA           VARCHAR2 (15 BYTE)  NOT NULL , 
     SUBALTERNO           VARCHAR2 (3 BYTE)  NOT NULL , 
     ALLEGATO             VARCHAR2 (1 BYTE)  NOT NULL , 
     SVILUPPO             VARCHAR2 (1 BYTE)  NOT NULL , 
     DATA_INIZIO_VALIDITA DATE  NOT NULL , 
     DATA_FINE_VALIDITA   DATE , 
     SHAPE                SDO_GEOMETRY  NOT NULL 
    ) 
COLUMN SHAPE NOT SUBSTITUTABLE AT ALL LEVELS
VARRAY "SHAPE"."SDO_ELEM_INFO" STORE AS LOB (tablespace SITIPIOPR_lob)
VARRAY "SHAPE"."SDO_ORDINATES" STORE AS LOB (tablespace SITIPIOPR_lob)
TABLESPACE SITIPIOPR_TBL;


ALTER TABLE QGIS_T_CXF_PARTICELLA 
    ADD CONSTRAINT PK_QGIS_T_CXF_PARTICELLA PRIMARY KEY ( ID_CXF_PARTICELLA  ) USING INDEX TABLESPACE SITIPIOPR_IDX;

CREATE SEQUENCE SEQ_QGIS_T_CXF_PARTICELLA 
START WITH 10056076 
    NOCACHE ;
	
INSERT INTO USER_SDO_GEOM_METADATA(TABLE_NAME, COLUMN_NAME, DIMINFO, SRID)
VALUES(
	'QGIS_T_CXF_PARTICELLA', 
	'SHAPE',
	SDO_DIM_ARRAY(
		SDO_DIM_ELEMENT ('X', 1310000, 2820000, 0.005),
		SDO_DIM_ELEMENT ('Y', 3930000, 5220000, 0.005)
	),
	NULL
);

COMMIT;
   
ALTER TABLE QGIS_T_PARTICELLA_LAVORAZIONE ADD 
    ( 
     IDENTIFICATIVO_PRATICA_ORIGINE VARCHAR2 (50 BYTE) 
    ) 
;


COMMENT ON COLUMN QGIS_T_PARTICELLA_LAVORAZIONE.IDENTIFICATIVO_PRATICA_ORIGINE IS 'Indica l''identificativo della pratica di origine che puo'' legare diversi documenti archiviati'
;

grant select on QGIS_T_CXF_PARTICELLA to smrgaa_rw;

CREATE INDEX IE2_QGIS_T_PARTICELLA_LAVORAZI ON QGIS_T_PARTICELLA_LAVORAZIONE
(EXT_ID_PARTICELLA)
TABLESPACE SITIPIOPR_IDX;

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


	

