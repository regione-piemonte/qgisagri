package it.csi.qgisagri.agriapi.config;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;

@Configuration
@EnableAsync
@EnableWebMvc
@ComponentScan(basePackages =
{ "it.csi.qgisagri.agriapi" })
public class BeansConfig implements ApplicationContextAware
{

  protected static final int        CACHE_PERIOD = 31556926; // one year
  @Autowired
  private static ApplicationContext applicationContext;

  public static Object getBean(String name)
  {
    return applicationContext.getBean(name);
  }

  @Override
  public void setApplicationContext(ApplicationContext context)
      throws BeansException
  {
    applicationContext = context;
  }

}
