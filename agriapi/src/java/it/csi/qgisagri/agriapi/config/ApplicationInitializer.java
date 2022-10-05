package it.csi.qgisagri.agriapi.config;

import org.springframework.web.servlet.support.AbstractAnnotationConfigDispatcherServletInitializer;

public class ApplicationInitializer
    extends AbstractAnnotationConfigDispatcherServletInitializer
{

  @Override
  protected Class<?>[] getRootConfigClasses()
  {
    return new Class[]
    { BeansConfig.class, DataSourceConfig.class, TransactionConfig.class};
  }

  @Override
  protected Class<?>[] getServletConfigClasses()
  {
    return new Class[]
        {};
  }

  @Override
  protected String[] getServletMappings()
  {
    return new String[]
    { "/siappcg/*" };
  }

}