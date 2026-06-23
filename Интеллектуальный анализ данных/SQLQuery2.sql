USE [AdventureWorksDW2014]
GO

/****** Object:  View [dbo].[vInternateSales]    Script Date: 14.04.2022 15:03:43 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[vInternateSales]
AS
SELECT        dbo.FactInternetSales.OrderDate, dbo.DimProductCategory.ProductCategoryAlternateKey, dbo.DimProductSubcategory.EnglishProductSubcategoryName, 
                         dbo.DimProductSubcategory.ProductCategoryKey, dbo.DimProductCategory.EnglishProductCategoryName, dbo.DimSalesTerritory.SalesTerritoryCountry, 
                         dbo.DimSalesTerritory.SalesTerritoryRegion, dbo.DimSalesTerritory.SalesTerritoryAlternateKey, dbo.DimSalesTerritory.SalesTerritoryGroup, 
                         dbo.DimCustomer.CustomerAlternateKey, dbo.DimCustomer.EmailAddress, dbo.DimCustomer.Gender, dbo.DimCustomer.MaritalStatus, 
                         dbo.FactInternetSales.SalesAmount, dbo.FactInternetSales.ProductKey, dbo.FactInternetSales.OrderDateKey, dbo.FactInternetSales.DueDateKey, 
                         dbo.FactInternetSales.ShipDateKey, dbo.FactInternetSales.CustomerKey, dbo.FactInternetSales.PromotionKey, dbo.FactInternetSales.CurrencyKey, 
                         dbo.FactInternetSales.SalesTerritoryKey, dbo.FactInternetSales.SalesOrderNumber, dbo.FactInternetSales.SalesOrderLineNumber, 
                         dbo.FactInternetSales.RevisionNumber, dbo.FactInternetSales.OrderQuantity, dbo.FactInternetSales.UnitPrice, dbo.FactInternetSales.ExtendedAmount, 
                         dbo.FactInternetSales.UnitPriceDiscountPct, dbo.FactInternetSales.DiscountAmount, dbo.FactInternetSales.ProductStandardCost, 
                         dbo.FactInternetSales.TotalProductCost, dbo.FactInternetSales.TaxAmt, dbo.FactInternetSales.Freight, dbo.FactInternetSales.CarrierTrackingNumber, 
                         dbo.FactInternetSales.CustomerPONumber, dbo.FactInternetSales.DueDate, dbo.FactInternetSales.ShipDate, dbo.DimProduct.ProductKey AS Expr1, 
                         dbo.DimProduct.ProductAlternateKey, dbo.DimProduct.ProductSubcategoryKey, dbo.DimProduct.WeightUnitMeasureCode, dbo.DimProduct.SizeUnitMeasureCode, 
                         dbo.DimProduct.EnglishProductName, dbo.DimProduct.SpanishProductName, dbo.DimProduct.FrenchProductName, dbo.DimProduct.StandardCost, 
                         dbo.DimProduct.FinishedGoodsFlag, dbo.DimProduct.Color, dbo.DimProduct.SafetyStockLevel, dbo.DimProduct.ReorderPoint, dbo.DimProduct.ListPrice, 
                         dbo.DimProduct.Size, dbo.DimProduct.SizeRange, dbo.DimProduct.Weight, dbo.DimProduct.DaysToManufacture, dbo.DimProduct.ProductLine, 
                         dbo.DimProduct.DealerPrice, dbo.DimProduct.Class, dbo.DimProduct.Style, dbo.DimProduct.ModelName, dbo.DimProduct.LargePhoto, 
                         dbo.DimProduct.EnglishDescription, dbo.DimProduct.FrenchDescription, dbo.DimProduct.ChineseDescription, dbo.DimProduct.ArabicDescription, 
                         dbo.DimProduct.HebrewDescription, dbo.DimProduct.ThaiDescription, dbo.DimProduct.GermanDescription, dbo.DimProduct.JapaneseDescription, 
                         dbo.DimProduct.TurkishDescription, dbo.DimProduct.StartDate, dbo.DimProduct.EndDate, dbo.DimProduct.Status, 
                         dbo.DimProductSubcategory.ProductSubcategoryKey AS Expr2, dbo.DimProductSubcategory.ProductSubcategoryAlternateKey, 
                         dbo.DimProductSubcategory.SpanishProductSubcategoryName, dbo.DimProductSubcategory.FrenchProductSubcategoryName, 
                         dbo.DimProductCategory.ProductCategoryKey AS Expr3, dbo.DimProductCategory.SpanishProductCategoryName, 
                         dbo.DimProductCategory.FrenchProductCategoryName, dbo.DimSalesTerritory.SalesTerritoryKey AS Expr4, dbo.DimSalesTerritory.SalesTerritoryImage, 
                         dbo.DimGeography.GeographyKey, dbo.DimGeography.City, dbo.DimGeography.StateProvinceCode, dbo.DimGeography.StateProvinceName, 
                         dbo.DimGeography.CountryRegionCode, dbo.DimGeography.EnglishCountryRegionName, dbo.DimGeography.SpanishCountryRegionName, 
                         dbo.DimGeography.FrenchCountryRegionName, dbo.DimGeography.PostalCode, dbo.DimGeography.SalesTerritoryKey AS Expr5, 
                         dbo.DimGeography.IpAddressLocator, dbo.DimPromotion.PromotionKey AS Expr6, dbo.DimPromotion.PromotionAlternateKey, 
                         dbo.DimPromotion.EnglishPromotionName, dbo.DimPromotion.SpanishPromotionName, dbo.DimPromotion.FrenchPromotionName, dbo.DimPromotion.DiscountPct, 
                         dbo.DimPromotion.EnglishPromotionType, dbo.DimPromotion.SpanishPromotionType, dbo.DimPromotion.FrenchPromotionType, 
                         dbo.DimPromotion.EnglishPromotionCategory, dbo.DimPromotion.SpanishPromotionCategory, dbo.DimPromotion.FrenchPromotionCategory, 
                         dbo.DimPromotion.StartDate AS Expr7, dbo.DimPromotion.EndDate AS Expr8, dbo.DimPromotion.MinQty, dbo.DimPromotion.MaxQty, 
                         dbo.DimCustomer.CustomerKey AS Expr9, dbo.DimCustomer.GeographyKey AS Expr10, dbo.DimCustomer.Title, dbo.DimCustomer.FirstName, 
                         dbo.DimCustomer.MiddleName, dbo.DimCustomer.LastName, dbo.DimCustomer.NameStyle, dbo.DimCustomer.BirthDate, dbo.DimCustomer.Suffix, 
                         dbo.DimCustomer.YearlyIncome, dbo.DimCustomer.TotalChildren, dbo.DimCustomer.NumberChildrenAtHome, dbo.DimCustomer.EnglishEducation, 
                         dbo.DimCustomer.SpanishEducation, dbo.DimCustomer.FrenchEducation, dbo.DimCustomer.EnglishOccupation, dbo.DimCustomer.SpanishOccupation, 
                         dbo.DimCustomer.FrenchOccupation, dbo.DimCustomer.HouseOwnerFlag, dbo.DimCustomer.NumberCarsOwned, dbo.DimCustomer.AddressLine1, 
                         dbo.DimCustomer.AddressLine2, dbo.DimCustomer.Phone, dbo.DimCustomer.DateFirstPurchase, dbo.DimCustomer.CommuteDistance, 
                         dbo.DimCurrency.CurrencyKey AS Expr11, dbo.DimCurrency.CurrencyAlternateKey, dbo.DimCurrency.CurrencyName, 
                         dbo.FactInternetSalesReason.SalesOrderNumber AS Expr12, dbo.FactInternetSalesReason.SalesOrderLineNumber AS Expr13, 
                         dbo.FactInternetSalesReason.SalesReasonKey, dbo.DimDate.DateKey, dbo.DimDate.FullDateAlternateKey, dbo.DimDate.DayNumberOfWeek, 
                         dbo.DimDate.EnglishDayNameOfWeek, dbo.DimDate.SpanishDayNameOfWeek, dbo.DimDate.FrenchDayNameOfWeek, dbo.DimDate.DayNumberOfMonth, 
                         dbo.DimDate.DayNumberOfYear, dbo.DimDate.WeekNumberOfYear, dbo.DimDate.EnglishMonthName, dbo.DimDate.SpanishMonthName, 
                         dbo.DimDate.FrenchMonthName, dbo.DimDate.MonthNumberOfYear, dbo.DimDate.CalendarQuarter, dbo.DimDate.CalendarYear, dbo.DimDate.CalendarSemester, 
                         dbo.DimDate.FiscalQuarter, dbo.DimDate.FiscalYear, dbo.DimDate.FiscalSemester
FROM            dbo.FactInternetSales INNER JOIN
                         dbo.DimProduct ON dbo.FactInternetSales.ProductKey = dbo.DimProduct.ProductKey INNER JOIN
                         dbo.DimProductSubcategory ON dbo.DimProduct.ProductSubcategoryKey = dbo.DimProductSubcategory.ProductSubcategoryKey INNER JOIN
                         dbo.DimProductCategory ON dbo.DimProductSubcategory.ProductCategoryKey = dbo.DimProductCategory.ProductCategoryKey INNER JOIN
                         dbo.DimSalesTerritory ON dbo.FactInternetSales.SalesTerritoryKey = dbo.DimSalesTerritory.SalesTerritoryKey INNER JOIN
                         dbo.DimGeography ON dbo.DimSalesTerritory.SalesTerritoryKey = dbo.DimGeography.SalesTerritoryKey INNER JOIN
                         dbo.DimPromotion ON dbo.FactInternetSales.PromotionKey = dbo.DimPromotion.PromotionKey INNER JOIN
                         dbo.DimCustomer ON dbo.FactInternetSales.CustomerKey = dbo.DimCustomer.CustomerKey AND 
                         dbo.DimGeography.GeographyKey = dbo.DimCustomer.GeographyKey INNER JOIN
                         dbo.DimCurrency ON dbo.FactInternetSales.CurrencyKey = dbo.DimCurrency.CurrencyKey INNER JOIN
                         dbo.FactInternetSalesReason ON dbo.FactInternetSales.SalesOrderNumber = dbo.FactInternetSalesReason.SalesOrderNumber AND 
                         dbo.FactInternetSales.SalesOrderLineNumber = dbo.FactInternetSalesReason.SalesOrderLineNumber INNER JOIN
                         dbo.DimDate ON dbo.FactInternetSales.OrderDateKey = dbo.DimDate.DateKey

GO

EXEC sys.sp_addextendedproperty @name=N'MS_DiagramPane1', @value=N'[0E232FF0-B466-11cf-A24F-00AA00A3EFFF, 1.00]
Begin DesignProperties = 
   Begin PaneConfigurations = 
      Begin PaneConfiguration = 0
         NumPanes = 4
         Configuration = "(H (1[50] 4[6] 2[17] 3) )"
      End
      Begin PaneConfiguration = 1
         NumPanes = 3
         Configuration = "(H (1 [50] 4 [25] 3))"
      End
      Begin PaneConfiguration = 2
         NumPanes = 3
         Configuration = "(H (1 [50] 2 [25] 3))"
      End
      Begin PaneConfiguration = 3
         NumPanes = 3
         Configuration = "(H (4 [30] 2 [40] 3))"
      End
      Begin PaneConfiguration = 4
         NumPanes = 2
         Configuration = "(H (1 [56] 3))"
      End
      Begin PaneConfiguration = 5
         NumPanes = 2
         Configuration = "(H (2 [66] 3))"
      End
      Begin PaneConfiguration = 6
         NumPanes = 2
         Configuration = "(H (4 [50] 3))"
      End
      Begin PaneConfiguration = 7
         NumPanes = 1
         Configuration = "(V (3))"
      End
      Begin PaneConfiguration = 8
         NumPanes = 3
         Configuration = "(H (1[56] 4[18] 2) )"
      End
      Begin PaneConfiguration = 9
         NumPanes = 2
         Configuration = "(H (1 [75] 4))"
      End
      Begin PaneConfiguration = 10
         NumPanes = 2
         Configuration = "(H (1[66] 2) )"
      End
      Begin PaneConfiguration = 11
         NumPanes = 2
         Configuration = "(H (4 [60] 2))"
      End
      Begin PaneConfiguration = 12
         NumPanes = 1
         Configuration = "(H (1) )"
      End
      Begin PaneConfiguration = 13
         NumPanes = 1
         Configuration = "(V (4))"
      End
      Begin PaneConfiguration = 14
         NumPanes = 1
         Configuration = "(V (2))"
      End
      ActivePaneConfig = 0
   End
   Begin DiagramPane = 
      Begin Origin = 
         Top = 0
         Left = 0
      End
      Begin Tables = 
         Begin Table = "FactInternetSales"
            Begin Extent = 
               Top = 6
               Left = 38
               Bottom = 135
               Right = 252
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimProduct"
            Begin Extent = 
               Top = 6
               Left = 290
               Bottom = 135
               Right = 512
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimProductSubcategory"
            Begin Extent = 
               Top = 6
               Left = 550
               Bottom = 135
               Right = 820
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimProductCategory"
            Begin Extent = 
               Top = 172
               Left = 0
               Bottom = 301
               Right = 252
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimSalesTerritory"
            Begin Extent = 
               Top = 176
               Left = 312
               Bottom = 305
               Right = 539
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimGeography"
            Begin Extent = 
               Top = 138
               Left = 593
               Bottom = 267
               Right = 835
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimPromotion"
            Begin Extent = 
               Top = 313
               Left = 38
               Bottom = 442
               Right =' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'VIEW',@level1name=N'vInternateSales'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_DiagramPane2', @value=N' 273
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimCustomer"
            Begin Extent = 
               Top = 6
               Left = 858
               Bottom = 135
               Right = 1081
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimCurrency"
            Begin Extent = 
               Top = 138
               Left = 873
               Bottom = 250
               Right = 1077
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "FactInternetSalesReason"
            Begin Extent = 
               Top = 330
               Left = 318
               Bottom = 442
               Right = 529
            End
            DisplayFlags = 280
            TopColumn = 0
         End
         Begin Table = "DimDate"
            Begin Extent = 
               Top = 292
               Left = 702
               Bottom = 421
               Right = 926
            End
            DisplayFlags = 280
            TopColumn = 0
         End
      End
   End
   Begin SQLPane = 
   End
   Begin DataPane = 
      Begin ParameterDefaults = ""
      End
      Begin ColumnWidths = 161
         Width = 284
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'VIEW',@level1name=N'vInternateSales'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_DiagramPane3', @value=N' = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
         Width = 1500
      End
   End
   Begin CriteriaPane = 
      Begin ColumnWidths = 11
         Column = 1440
         Alias = 900
         Table = 1170
         Output = 720
         Append = 1400
         NewValue = 1170
         SortType = 1350
         SortOrder = 1410
         GroupBy = 1350
         Filter = 1350
         Or = 1350
         Or = 1350
         Or = 1350
      End
   End
End
' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'VIEW',@level1name=N'vInternateSales'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_DiagramPaneCount', @value=3 , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'VIEW',@level1name=N'vInternateSales'
GO


