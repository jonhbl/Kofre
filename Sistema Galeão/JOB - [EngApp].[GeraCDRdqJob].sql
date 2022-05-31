USE [PortalOperacaoDB]
GO

/****** Object:  StoredProcedure [EngApp].[GeraCDRdqJob]    Script Date: 27/05/2022 14:49:18 ******/
SET ANSI_NULLS OFF
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE PROCEDURE [EngApp].[GeraCDRdqJob]
AS
BEGIN
	/* Altaração: 19/03/2022 Motivo: Documentação ID: 001 */

  DECLARE @DataInicial as DATETIME
  DECLARE @DataFinal as DATETIME
  DECLARE @NmTabela as VARCHAR(50)

  DECLARE @i as INT
  DECLARE @Consulta as VARCHAR(2000)

  CREATE TABLE #Datas
  (
  Tabela varchar(80),
  [Data] datetime NULL,
  DataRef datetime
  )

  DECLARE CDRTables CURSOR READ_ONLY --001: Cursor com todas as tabelas CDR
	FOR
  	SELECT Rcdr.NomeTabelaCDR from engapp.Relaccdr Rcdr

  OPEN CDRTables

  FETCH NEXT FROM CDRTables
  INTO @NmTabela

  WHILE @@FETCH_STATUS = 0 --001: Faça para todas as tabelas CDR
  BEGIN

    Set @Consulta = 'Select  top 1 ''' + @NmTabela + ''', Data, CONVERT(VARCHAR(10), Data, 120) from engapp.' + @NmTabela + ' order by data desc'
    insert into #Datas exec(@Consulta); 
	--001: Contula para traser a DATA FINAL de referência da tabela CDR

    Set @Consulta = 'Select  top 1 ''' + @NmTabela + '_dq'', Data, CONVERT(VARCHAR(10), DATEADD(dd,1,Data), 120) from engapp.' + @NmTabela + '_dq order by data desc'
    insert into #Datas exec(@Consulta);
	--001: Contula para traser a DATA INICIAL de referência da tabela CDR_dq

	set @DataInicial = ISNULL((Select top 1 DATEADD(s,0,Dataref) from #Datas where Tabela = @NmTabela + '_dq'), 0)
    Select @DataFinal = DATEADD(s,-1,DATEADD(dd,1,Dataref)) from #Datas where Tabela = @NmTabela
	--001: Conversão das datas

    if(@DataInicial < @DataFinal)
    BEGIN
    	EXEC EngApp.GeraCDRdqT88 @DataInicial,@DataFinal,@NmTabela
    END

	FETCH NEXT FROM CDRTables
  	INTO @NmTabela
  END

  CLOSE CDRTables;
  DEALLOCATE CDRTables;
  DROP Table #Datas;

END

GO


