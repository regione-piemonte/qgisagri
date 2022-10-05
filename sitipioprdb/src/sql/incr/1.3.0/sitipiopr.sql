set define off;

alter table QGIS_T_SUOLO_LAVORAZIONE add (EXT_ID_UTENTE_LAVORAZIONE NUMBER(10) );

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


	

