USE [PortalOperacaoDB]
GO

/****** Object:  Table [EngApp].[cdr0014_dq]    Script Date: 27/05/2022 14:44:31 ******/
SET ANSI_NULLS OFF
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [EngApp].[cdr0014_dq](
	[Data] [datetime] NULL,
	[ID] [int] NOT NULL,
	[Talkgroup] [int] NOT NULL,
	[CodEvento] [int] NOT NULL,
	[Duracao_H0] [float] NULL,
	[Quantidade_H0] [int] NULL,
	[Duracao_H1] [float] NULL,
	[Quantidade_H1] [int] NULL,
	[Duracao_H2] [float] NULL,
	[Quantidade_H2] [int] NULL,
	[Duracao_H3] [float] NULL,
	[Quantidade_H3] [int] NULL,
	[Duracao_H4] [float] NULL,
	[Quantidade_H4] [int] NULL,
	[Duracao_H5] [float] NULL,
	[Quantidade_H5] [int] NULL,
	[Duracao_H6] [float] NULL,
	[Quantidade_H6] [int] NULL,
	[Duracao_H7] [float] NULL,
	[Quantidade_H7] [int] NULL,
	[Duracao_H8] [float] NULL,
	[Quantidade_H8] [int] NULL,
	[Duracao_H9] [float] NULL,
	[Quantidade_H9] [int] NULL,
	[Duracao_H10] [float] NULL,
	[Quantidade_H10] [int] NULL,
	[Duracao_H11] [float] NULL,
	[Quantidade_H11] [int] NULL,
	[Duracao_H12] [float] NULL,
	[Quantidade_H12] [int] NULL,
	[Duracao_H13] [float] NULL,
	[Quantidade_H13] [int] NULL,
	[Duracao_H14] [float] NULL,
	[Quantidade_H14] [int] NULL,
	[Duracao_H15] [float] NULL,
	[Quantidade_H15] [int] NULL,
	[Duracao_H16] [float] NULL,
	[Quantidade_H16] [int] NULL,
	[Duracao_H17] [float] NULL,
	[Quantidade_H17] [int] NULL,
	[Duracao_H18] [float] NULL,
	[Quantidade_H18] [int] NULL,
	[Duracao_H19] [float] NULL,
	[Quantidade_H19] [int] NULL,
	[Duracao_H20] [float] NULL,
	[Quantidade_H20] [int] NULL,
	[Duracao_H21] [float] NULL,
	[Quantidade_H21] [int] NULL,
	[Duracao_H22] [float] NULL,
	[Quantidade_H22] [int] NULL,
	[Duracao_H23] [float] NULL,
	[Quantidade_H23] [int] NULL,
	[site] [int] NULL
) ON [PRIMARY]
GO

ALTER TABLE [EngApp].[cdr0014_dq] ADD  DEFAULT ((0)) FOR [ID]
GO

ALTER TABLE [EngApp].[cdr0014_dq] ADD  DEFAULT ((0)) FOR [Talkgroup]
GO


