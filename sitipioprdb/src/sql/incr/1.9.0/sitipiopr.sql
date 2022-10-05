set define off;

alter table QGIS_T_SUOLO_PROPOSTO add EXT_ID_PROCEDIMENTO NUMBER (4) ;
alter table QGIS_T_SUOLO_PROPOSTO add CLASSIFICAZIONE_ARCHIVIO_SIAP VARCHAR2 (100) ;
alter table QGIS_T_SUOLO_PROPOSTO add IDENTIFICATIVO_PRATICA VARCHAR2 (20) ; 
alter table QGIS_T_SUOLO_PROPOSTO add EXT_ID_AMM_COMPETENZA NUMBER (4) ;
alter table QGIS_T_SUOLO_PROPOSTO add DESCRIZIONE_BANDO VARCHAR2 (500) ; 
alter table QGIS_T_SUOLO_PROPOSTO add NUMERO_BANDO_DOC VARCHAR2 (500) ; 
alter table QGIS_T_SUOLO_PROPOSTO add GRUPPO_IDENTIFICATIVO VARCHAR2 (500) ;

COMMENT ON COLUMN QGIS_T_SUOLO_PROPOSTO.EXT_ID_PROCEDIMENTO IS 'Indica il procedimento (applicativo) di provenienza' 
;

COMMENT ON COLUMN QGIS_T_SUOLO_PROPOSTO.CLASSIFICAZIONE_ARCHIVIO_SIAP IS 'Indica il codice di classificazione per l''archiviazione del documento in Archivio SIAP' 
;

COMMENT ON COLUMN QGIS_T_SUOLO_PROPOSTO.IDENTIFICATIVO_PRATICA IS 'Indica l''identificativo pratica del procedimento di provenienza' 
;

COMMENT ON COLUMN QGIS_T_SUOLO_PROPOSTO.EXT_ID_AMM_COMPETENZA IS 'Indica l''amministrazione di competenza della pratica del procedimento di provenienza' 
;

COMMENT ON COLUMN QGIS_T_SUOLO_PROPOSTO.DESCRIZIONE_BANDO IS 'Descrizione del bando legato alla pratica del procedimento di provenienza' 
;

COMMENT ON COLUMN QGIS_T_SUOLO_PROPOSTO.NUMERO_BANDO_DOC IS 'Numero del bando legato alla pratica del procedimento di provenienza' 
;

COMMENT ON COLUMN QGIS_T_SUOLO_PROPOSTO.GRUPPO_IDENTIFICATIVO IS 'Capofila del procedimento legato alla pratica del procedimento di provenienza' 
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


	

