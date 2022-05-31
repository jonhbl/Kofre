USE [PortalOperacaoDB]
GO

/****** Object:  Table [EngApp].[cdr0014]    Script Date: 27/05/2022 14:44:08 ******/
SET ANSI_NULLS OFF
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [EngApp].[cdr0014](
	[Data] [datetime] NULL,
	[ID] [nvarchar](45) NULL,
	[Grupo] [nvarchar](45) NULL,
	[Canal] [nvarchar](45) NULL,
	[Evento] [nvarchar](max) NULL,
	[CodEvento] [int] NULL,
	[Duracao] [float] NULL,
	[site] [int] NULL,
 CONSTRAINT [cdr0014_uq] UNIQUE CLUSTERED 
(
	[Data] ASC,
	[ID] ASC,
	[Grupo] ASC,
	[Canal] ASC,
	[Duracao] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

ALTER TABLE [EngApp].[cdr0014]  WITH CHECK ADD  CONSTRAINT [cdr0014_fk] FOREIGN KEY([CodEvento])
REFERENCES [EngApp].[relacEventos] ([ID])
GO

ALTER TABLE [EngApp].[cdr0014] CHECK CONSTRAINT [cdr0014_fk]
GO


